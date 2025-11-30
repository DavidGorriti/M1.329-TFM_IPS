import os
import logging

# Carpetas de origen y destino de los datos
SOURCE_FOLDER = 'RawData'
DESTINY_FOLDER = 'ProcessedData'

# Nombres de ficheros de los que hay que estimar la posición
SHOULD_ESTIMATE_POSITION_FILENAME = 'TrainingTrial'
FLOOR_TRANSITION_FILENAME = SHOULD_ESTIMATE_POSITION_FILENAME + '5'

# Prefijo de los ficheros Ground Truth
GROUND_TRUTH_PREFIX = 'GT_'

# Cadenas de texto de los datos
POSI_STR = 'POSI'
WIFI_STR = 'WIFI'

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Redondea el timestampo a 3 decimales
def roundTimestamp(timestamp):
    return str(round(float(timestamp), 3))

# Redondea el timestamp de POSI
def processPosiLine(line):
    fields = line.split(';')
    fields[1] = roundTimestamp(fields[1])
    return ';'.join(fields)
    
# Redondea lostimestamps de WIFI
def processWifiLine(line):
    fields = line.split(';')
    fields[1] = roundTimestamp(fields[1])
    fields[2] = roundTimestamp(fields[2])
    return ';'.join(fields)

# Redondea el timestamp de POSI
def processGroundTruthPosiLine(line):
    finalFields = []
    fields = line.split(',')
    
    finalFields = [
        POSI_STR,
        roundTimestamp(fields[0]),
        str(int(fields[4].strip())),
        fields[2],
        fields[1],
        str(int(fields[3])),
        '100'
    ]
    return ';'.join(finalFields) + '\n'

# Obtiene las líneas POSI y WIFI de los ficheros
def getPosiAndWifiLines(file_path):   
    posi_lines = []
    wifi_lines = []
    
    # Leer el archivo original y filtrar líneas
    try:
        with open(file_path, 'r', encoding='utf-8') as src:
            for line in src:
                if line.startswith(POSI_STR):
                    posi_lines.append(processPosiLine(line))
                elif line.startswith(WIFI_STR):
                    wifi_lines.append(processWifiLine(line))
    except Exception as e:
        logging.error(f"Error reading '{source_path}': {e}")
    
    return posi_lines, wifi_lines

# Obtiene las líneas POSI del fichero Ground Truth
def getPosiFromGroundTruth(file_path):   
    posi_lines = []
    
    # Leer el archivo original y filtrar líneas
    try:
        with open(file_path, 'r', encoding='utf-8') as src:
            for line in src:
                posi_lines.append(processGroundTruthPosiLine(line))
    except Exception as e:
        logging.error(f"Error reading '{source_path}': {e}")
    
    return posi_lines

# Escribe el contenido en un fichero
def writeToFile(file_path, content):
    try:
        with open(file_path, 'w', encoding='utf-8') as out:
            out.writelines(content)
        logging.info(f"Written '{file_path}'")
    except Exception as e:
        logging.error(f"Error writing '{file_path}': {e}")

# Devuelve la línea POSI en una tupla
def parsePosiLine(posi_line):
    fields = posi_line.strip().split(';')
    timestamp = float(fields[1])
    counter = int(fields[2])
    lat = float(fields[3])
    lon = float(fields[4])
    floor = fields[5]
    building = fields[6]
    return (timestamp,counter,lat,lon,floor,building)

def estimatePositionsBetweenTwoPoints(estimated_posis,posi_line_1, posi_line_2):
    
    # Crear interpolaciones lineales cada milisegundo
    # P(t) = P1 + ((t)/delta_t) * (P2 - P1)
    t1 = posi_line_1[0]
    lat1 = posi_line_1[2]
    lon1 = posi_line_1[3]
    
    t2 = posi_line_2[0]
    lat2 = posi_line_2[2]
    lon2 = posi_line_2[3]
    
    start_ms = int(t1 * 1000)
    end_ms = int(t2 * 1000)
    delta_t = end_ms - start_ms
    
    for ms in range(start_ms + 1, end_ms):
        t = ms - start_ms
        lat = lat1 + (t / delta_t) * (lat2 - lat1)
        lon = lon1 + (t / delta_t) * (lon2 - lon1)
        
        estimated_posis.append(f"POSI;{ms/1000};-1;{lat};{lon};{posi_line_1[4]};{posi_line_1[5]}\n")
    

# Estima las posiciones con una interpolación lineal
def estimatePositions(posi_lines):
    
    logging.info("Estimating positions")
    
    estimated_posis = []
    
    for i in range(len(posi_lines) - 1):
        posi_line_1 = parsePosiLine(posi_lines[i])
        posi_line_2 = parsePosiLine(posi_lines[i + 1])
        
        # Añadir el primer POSI
        estimated_posis.append(posi_lines[i])
        
        estimatePositionsBetweenTwoPoints(estimated_posis,posi_line_1,posi_line_2)
    
    # Añadir el útimo POSI
    estimated_posis.append(posi_lines[len(posi_lines) - 1])
    
    return estimated_posis

# Estima las posiciones con una interpolación lineal, pero descartando las transiciones entre plantas
# TODO Descartar las transiciones entre plantas
def estimatePositionsWithoutTransitions(posi_lines):
    
    logging.info("Estimating positions")
    
    estimated_posis = []
    last_add_index = -1;
    
    for i in range(len(posi_lines) - 1):
        posi_line_1 = parsePosiLine(posi_lines[i])
        posi_line_2 = parsePosiLine(posi_lines[i + 1])
        
        # Estima las posiciones si las plantas de los dos puntos son iguales
        if posi_line_1[4] == posi_line_2[4]:
            
            # Añadir el primer POSI 
            if (i - 1 != last_add_index):
                estimated_posis.append(posi_lines[i])
            
            # TODO ¿Como añadir la última línea? Afecta al estimate anterior?
            estimatePositionsBetweenTwoPoints(estimated_posis,posi_line_1,posi_line_2)
            
            # Añadir el segundo POSI
            estimated_posis.append(posi_lines[i + 1])
            
            last_add_index = i;
    
    return estimated_posis

# Comprueba si hay que estimar las posiciones   
def shouldEstimatePositions(fileName):
    return SHOULD_ESTIMATE_POSITION_FILENAME in fileName
    
# Comprueba si tiene transiciones entre plantas
def isFloorTransitionFile(fileName):
    return FLOOR_TRANSITION_FILENAME in fileName
    
# Comprueba si el fichero es de coordenadas Ground Truth
def isGroundTruthFile(fileName):
    return fileName.startswith(GROUND_TRUTH_PREFIX)
        
def processFile(root, target_directory, file):
    source_path = os.path.join(root, file)
    base, ext = os.path.splitext(file)
    
    # Si no es fichero Ground Truth
    if not isGroundTruthFile(base):
        final_folder = os.path.join(target_directory, base)
        # Obtener la líneas POIS y WIFI
        posi_lines,wifi_lines = getPosiAndWifiLines(source_path)

        # Crear carpeta si hay contenido
        if posi_lines or wifi_lines:
            os.makedirs(final_folder, exist_ok=True)
            logging.info(f"'{final_folder}' directory created")
            
        # Crear archivos solo si hay contenido
        if wifi_lines:
            wifi_path = os.path.join(final_folder, f'{WIFI_STR}{ext}')
            writeToFile(wifi_path,wifi_lines)
            
        if posi_lines:
            posi_path = os.path.join(final_folder, f'{POSI_STR}{ext}')
            if shouldEstimatePositions(base):
                posi_path = os.path.join(final_folder, f'{POSI_STR}_tmp{ext}')
            
            writeToFile(posi_path,posi_lines)
            
            if shouldEstimatePositions(base):
                estimated_posis = []
                if isFloorTransitionFile(base):
                    estimated_posis = estimatePositionsWithoutTransitions(posi_lines)
                else:
                    estimated_posis = estimatePositions(posi_lines)
                    
                estimated_posi_path = os.path.join(final_folder, f'{POSI_STR}{ext}')
                writeToFile(estimated_posi_path,estimated_posis)
    # Si es fichero Ground Truth
    else:
        final_folder = os.path.join(target_directory, base.removeprefix(GROUND_TRUTH_PREFIX))
        os.makedirs(final_folder, exist_ok=True)
        posi_lines = getPosiFromGroundTruth(source_path)
        posi_path = os.path.join(final_folder, f'{POSI_STR}.txt')
        writeToFile(posi_path,posi_lines)
        
def processData():
    logging.info('DATA PROCESSING STARTED')

    for root, dirs, files in os.walk(SOURCE_FOLDER):
        relative_path = os.path.relpath(root, SOURCE_FOLDER)
        target_directory = os.path.join(DESTINY_FOLDER, relative_path)
        os.makedirs(target_directory, exist_ok=True)
        
        logging.info('\n//////////////////////////////////////////////////////////')
        logging.info(f"'{target_directory}' directory created")

        for file in files:
            processFile(root, target_directory, file)
            
    logging.info('DATA PROCESSING FINISHED')
    
processData()