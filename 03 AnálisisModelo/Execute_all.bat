@echo off

echo Ejecutando 01-Train2DModel_split8020.py...
py "01-Train2DModel_split8020.py"

echo Ejecutando 01-Train2DModel.py...
py "01-Train2DModel.py"

echo Ejecutando 01-Train2DModel_testing.py...
py "01-Train2DModel_testing.py"

echo Ejecutando 01-Train2DModel_scoring.py...
py "01-Train2DModel_scoring.py"

echo Ejecutando 02-TrainFloorDetectionModel_split8020.py...
py "02-TrainFloorDetectionModel_split8020.py"

echo Ejecutando 02-TrainFloorDetectionModel.py...
py "02-TrainFloorDetectionModel.py"

echo Ejecutando 02-TrainFloorDetectionModel_testing.py...
py "02-TrainFloorDetectionModel_testing.py"

echo Ejecutando 02-TrainFloorDetectionModel_scoring.py...
py "02-TrainFloorDetectionModel_scoring.py"

echo Todos los scripts se han ejecutado.