import logging
import psycopg

DELETE_FROM = "DELETE FROM tfm_ips.ReferencePointsPositionWifi"

INSERT_INTO_PART =  """INSERT INTO tfm_ips.ReferencePointsPositionWifi (
                        originalfileid,
                        posiapptimestamp,
                        wifiapptimestamp,
                        mac_bssid,
                        rss,
                        latitude,
                        longitude,
                        floorid
                    )"""

SELECT_FROM_TRAINING =   """SELECT posi.originalfileid,posi.apptimestamp,wifi.apptimestamp,wifi.mac_bssid,wifi.rss,posi.latitude,posi.longitude,posi.floorid
                                    FROM tfm_ips.referencepointswifi wifi 
                                    join tfm_ips.referencepointsposition posi 
                                        on wifi.originalfileid = posi.originalfileid
                                        and wifi.apptimestamp = posi.apptimestamp
                                    join tfm_ips.originalfile 
                                        ON originalfile.id = wifi.originalfileid 
                                        and originalfile.filename like '%TrainingTrial%';"""
                    
SELECT_FROM_TESTING_SCORING = """SELECT posi.originalfileid,posi.apptimestamp,wifi.apptimestamp,wifi.mac_bssid,wifi.rss,posi.latitude,posi.longitude,posi.floorid
                                    FROM tfm_ips.referencepointsposition posi
                                    -- Para obtener las medicions WIFI anteriores más cercanas
                                    JOIN LATERAL (
                                        SELECT MAX(w.apptimestamp) AS max_wifi_ts
                                        FROM tfm_ips.referencepointswifi w
                                        WHERE w.originalfileid = posi.originalfileid
                                          AND w.apptimestamp < posi.apptimestamp
                                    ) m ON m.max_wifi_ts IS NOT NULL
                                    JOIN tfm_ips.referencepointswifi wifi
                                      ON wifi.originalfileid = posi.originalfileid
                                     AND wifi.apptimestamp = m.max_wifi_ts
                                    JOIN tfm_ips.originalfile ofile
                                      ON ofile.id = posi.originalfileid
                                     AND ofile.filename NOT LIKE '%TrainingTrial%';"""                        

UPDATE_PROJECTED_COORDINATES = """WITH minCoordinates AS (
                                    SELECT 
                                        MIN(latitude) AS lat0,
                                        MIN(longitude) AS lon0
                                    FROM tfm_ips.ReferencePointsPosition
                                )
                                UPDATE tfm_ips.ReferencePointsPositionWifi
                                SET
                                    projectedx = 6371000 * 2 * 
                                        asin(
                                            sqrt(
                                                sin(radians(0)/2)^2 + 
                                                cos(radians(mc.lat0)) * cos(radians(mc.lat0)) * sin(radians(longitude - mc.lon0)/2)^2
                                            )
                                        ),
                                    projectedy = 6371000 * 2 * 
                                        asin(
                                            sqrt(
                                                sin(radians(latitude - mc.lat0)/2)^2 + 
                                                cos(radians(mc.lat0)) * cos(radians(latitude)) * sin(radians(0)/2)^2
                                            )
                                        )
                                FROM minCoordinates mc;
                                """

CONN = psycopg.connect(
    dbname="postgres",
    user="postgres",
    password="admin",
    host="localhost",
    port="5432"
)

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Ejecuta el query
def executeQuery(query):
    with CONN.cursor() as cur:
        cur.execute(query)

# Vacia la tabla ReferencePointsPositionWifi
def emptyTable():
    logging.info(f"Emptying ReferencePointsPositionWifi table")
    executeQuery(DELETE_FROM)

# Inserta las relaciones POSI y WIFI en la tabla ReferencePointsPositionWifi
def loadTable():
    logging.info(f"Loading table ReferencePointsPositionWifi from Training Trials")
    executeQuery(INSERT_INTO_PART + SELECT_FROM_TRAINING)
    logging.info(f"Loading table ReferencePointsPositionWifi from Testing and Scoring Trials")
    executeQuery(INSERT_INTO_PART + SELECT_FROM_TESTING_SCORING)

def calculateProjectedCoordinates():
    logging.info(f"Calculating projected coordinates for ReferencePointsPositionWifi")
    executeQuery(UPDATE_PROJECTED_COORDINATES)
    
def loadData():
    
    logging.info('TABLE LOADING STARTED')
    
    try:
        emptyTable()
        loadTable()
        calculateProjectedCoordinates()
        
        CONN.commit()
        
    except Exception as e:
        logging.error(f"Error loading table: {e}")
        CONN.rollback()
    finally:
        CONN.close()
        
    logging.info('TABLE LOADING FINISHED')

loadData()