import joblib
import pandas as pd
import numpy as np
from config.config import Config
from typing import Dict
from models.estimate_position_request import EstimatePositionRequest

class KNNService:
    # Cargar configuración de modelos
    config = Config()

    def __init__(self):
        # Modelos 2D
        models_2d = self.config.models_2d
        self.knn_2d = joblib.load(models_2d["knn"])
        self.scaler_2d = joblib.load(models_2d["scaler"])
        self.columns_2d = pd.read_csv(models_2d["columns"], header=None).values.flatten().tolist()

        # Modelos Floor Detection
        models_fd = self.config.models_fd
        self.knn_floor = joblib.load(models_fd["knn"])
        self.scaler_floor = joblib.load(models_fd["scaler"])
        self.columns_floor = pd.read_csv(models_fd["columns"], header=None).values.flatten().tolist()

    def _prepare_input(self, wifi_fingerprints: Dict[str, float], columns: list, scaler):
        # Rellena las columnas que faltan con -120 y escala con el scaler.
        X_df = pd.DataFrame([wifi_fingerprints])
        X_df = X_df.reindex(columns=columns, fill_value=-120)
        X_scaled = scaler.transform(X_df)
        return X_scaled

    def estimate_2d(self, wifi_fingerprints: Dict[str, float]):
        # Estima latitud y longitud usando KNN 2D.
        X_scaled = self._prepare_input(wifi_fingerprints, self.columns_2d, self.scaler_2d)
        position = self.knn_2d.predict(X_scaled)[0]
        return {"latitude": float(position[0]), "longitude": float(position[1])}

    def estimate_floor(self, wifi_fingerprints: Dict[str, float]):
        # Estima la planta usando KNN Floor Detection.
        X_scaled = self._prepare_input(wifi_fingerprints, self.columns_floor, self.scaler_floor)
        floor_id = self.knn_floor.predict(X_scaled)[0]
        return {"floorId": int(floor_id)}

    def estimate_2d_floor(self, request: EstimatePositionRequest):
        # Recibe un EstimatePositionRequest y devuelve latitud, longitud y floorId.
        # Convertir lista de WifiMeasurement a diccionario {mac_bssid: rssi}
        sorted_measurements = sorted(request.wifi_measurements, key=lambda measurement: measurement.mac_bssid)
        wifi_dict = {measurement.mac_bssid: measurement.rssi for measurement in sorted_measurements}

        # Estimaciones
        position_2d = self.estimate_2d(wifi_dict)
        floor = self.estimate_floor(wifi_dict)

        # Combinar resultados
        result = {**position_2d, **floor}
        return result