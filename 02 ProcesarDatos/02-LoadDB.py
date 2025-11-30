import os
import logging
import psycopg

POSI_STR = 'POSI'
WIFI_STR = 'WIFI'

DATA_FOLER = 'ProcessedData'
TEMP_FOLDER = 'tmp'

POSI_FILE_NAME = 'POSI.txt'
WIFI_FILE_NAME = 'WIFI.txt'

TEMP_POSI_FILE_NAME = os.path.join(TEMP_FOLDER, f'{POSI_FILE_NAME}')
TEMP_WIFI_FILE_NAME = os.path.join(TEMP_FOLDER, f'{WIFI_FILE_NAME}')

DELETE_ORIGINALFILE_SQL = "DELETE FROM tfm_ips.OriginalFile WHERE filename = %s;"
INSERT_ORIGINALFILE_SQL = "INSERT INTO tfm_ips.OriginalFile(filename) VALUES (%s) RETURNING Id;"

POSI_TABLE_NAME = "tfm_ips.referencepointsposition"
WIFI_TABLE_NAME = "tfm_ips.referencepointswifi"
POSI_TABLE_COLUMNS = ("originalfileid", "apptimestamp","counter","latitude","longitude","floorid","buildingid")
WIFI_TABLE_COLUMNS = ("originalfileid"," apptimestamp","sensortimestamp","name_ssid","mac_bssid","frequency","rss")

DB_LOAD_CHUNK_SIZE = 10 * 1024 * 1024

CONN = psycopg.connect(
    dbname="postgres",
    user="postgres",
    password="admin",
    host="localhost",
    port="5432"
)

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Elimina el nombre del fichero de la tabla junto con sus datos (FK DELETE CASCADE)
def deleteOriginalFileFromTable(filename):
    logging.info(f"Deleting '{filename}' from OriginalFile table")
    with CONN.cursor() as cur:
        cur.execute(DELETE_ORIGINALFILE_SQL, (filename,))

# Añade le nombre del fichero a la tabla
def insertOriginalFileTable(filename):
    logging.info(f"Inserting '{filename}' into OriginalFile table")
    with CONN.cursor() as cur:
        cur.execute(INSERT_ORIGINALFILE_SQL, (filename,))
        originalFileId = cur.fetchone()[0]
        logging.info(f"New originalFileId: '{originalFileId}'")
    return originalFileId

# Carga el fichero temporal en la tabla correspondiente
def loadFileToTable(sourceFile, tableName, colums):
    logging.info(f"Loading file '{sourceFile}' into '{tableName}' table")
    chunkCount = 1
    with open(sourceFile, "r", encoding="utf-8") as src:
        with CONN.cursor() as cur:
            with cur.copy(f"COPY {tableName} ({', '.join(colums)}) FROM STDIN WITH (FORMAT text, DELIMITER ';')") as copy:
                 while data := src.read(DB_LOAD_CHUNK_SIZE):
                    logging.info(f"Chunk number: {chunkCount}")
                    chunkCount = chunkCount + 1
                    copy.write(data)

# Agrega todos los datos del fichero de origen al final del fichero de destino
def copyFile(sourceFile, destinyFile, textToReplace, replacementText):
    with open(sourceFile, "r", encoding="utf-8") as src, \
        open(destinyFile, "a", encoding="utf-8") as dst:
        for line in src:
            dst.write(line.replace(textToReplace, replacementText))

# Envía los datos POSI al fichero temporal    
def createPosiTempFile(originalFileId, file):
    logging.info(f"Inserting '{file}' into ReferencePointsPosition table")
    copyFile(file,TEMP_POSI_FILE_NAME,POSI_STR,str(originalFileId))
    
# Envía los datos WIFI al fichero temporal    
def createWifiTempFile(originalFileId, file):
    logging.info(f"Inserting '{file}' into ReferencePointsWifi table")
    copyFile(file,TEMP_WIFI_FILE_NAME,WIFI_STR,str(originalFileId))

# Elimina los ficheros temporales
def deleteTempFiles():
    if os.path.exists(TEMP_POSI_FILE_NAME):
        os.remove(TEMP_POSI_FILE_NAME)
        logging.info(f"Temp file '{TEMP_POSI_FILE_NAME}' removed")
    if os.path.exists(TEMP_WIFI_FILE_NAME):
        os.remove(TEMP_WIFI_FILE_NAME)
        logging.info(f"Temp file '{TEMP_WIFI_FILE_NAME}' removed")

def loadData():
    logging.info('DATA LOADING STARTED')
    
    try:
        deleteTempFiles()
        
        for root, dirs, files in os.walk(DATA_FOLER):
            posiFile = os.path.join(root, POSI_FILE_NAME)
            wifiFile = os.path.join(root, WIFI_FILE_NAME)
            if os.path.exists(posiFile) and os.path.exists(wifiFile):
                logging.info(f"-------------- LOADING ---------------------- '{posiFile}' and '{wifiFile}' into ReferencePointsPosition table")
                logging.info(f"    - '{posiFile}'")
                logging.info(f"    - '{wifiFile}'")
                
                originalFileName = os.path.basename(root)
                deleteOriginalFileFromTable(originalFileName)
                originalFileId = insertOriginalFileTable(originalFileName)
                
                createPosiTempFile(originalFileId, posiFile)
                createWifiTempFile(originalFileId, wifiFile)
                
        loadFileToTable(TEMP_POSI_FILE_NAME, POSI_TABLE_NAME, POSI_TABLE_COLUMNS)
        loadFileToTable(TEMP_WIFI_FILE_NAME, WIFI_TABLE_NAME, WIFI_TABLE_COLUMNS)
        
        CONN.commit()
        
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        CONN.rollback()
    finally:
        CONN.close()
        
    logging.info('DATA LOADING FINISHED')
    
loadData()