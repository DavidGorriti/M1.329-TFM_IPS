import psycopg
import logging
import pandas as pd
import numpy as np
import joblib
import json

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor

MODELS_FOLDER = 'models'

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("Training.log"),
        logging.StreamHandler()
    ]
)
    
def get_connection():
    return psycopg.connect(
        dbname="postgres",
        user="postgres",
        password="admin",
        host="localhost",
        port="5432"
    )
    
def train_2d_model(sql_columns, sql_training, knn_params, model_filename_prefix):
    df_cols = read_sql(sql_columns)
    df_train = read_sql(sql_training)

    X_train_scaled, y_train, scaler = get_datasets_2d(df_cols, df_train)

    logging_info(f"X_train_scaled shape: {X_train_scaled.shape}")
    logging_info(f"y_train shape: {y_train.shape}")

    # Configurar y entrenar modelo KNN
    knn = train_KNN_Regressor(X_train_scaled, y_train, knn_params)
    save_model_to_disk(knn, scaler, df_cols, model_filename_prefix)
    
def train_floor_detection_model(sql_columns, sql_training, knn_params, model_filename_prefix):
    df_cols = read_sql(sql_columns)
    df_train = read_sql(sql_training)

    X_train_scaled, y_train, scaler = get_datasets_floor_detection(df_cols, df_train)

    logging_info(f"X_train_scaled shape: {X_train_scaled.shape}")
    logging_info(f"y_train shape: {y_train.shape}")

    # Configurar y entrenar modelo KNN
    knn = train_KNN_Classifier(X_train_scaled, y_train, knn_params)
    save_model_to_disk(knn, scaler, df_cols, model_filename_prefix)

def read_sql(sql):
    conn = get_connection()
    df = pd.read_sql(sql, conn)
    conn.close()
    return df

def get_x_scaled(X_train):
    # Escalar los valores
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    return X_train_scaled, scaler

def get_x_datasets(df_cols, df_train):
    # Pivotar el conjunto de tablas. Cada fila son las coordenadas y cada columna un punto de acceso. Los valores son el RSSI
    X_train = df_train.pivot_table(
        index="id",
        columns="mac_bssid",
        values="rss",
        fill_value=-120
    )

    # Alinear columnas para asegurar que no falten columnas
    X_train = X_train.reindex(columns=df_cols["mac_bssid"].tolist(), fill_value=-120)
    
    # Escalar los valores
    X_train_scaled, scaler = get_x_scaled(X_train)
    
    return X_train_scaled, scaler

def get_datasets_2d(df_cols, df_train):

    X_train_scaled, scaler = get_x_datasets(df_cols, df_train)
    
    # Crear las etiquetas
    y_train = df_train.drop_duplicates("id").set_index("id")[["latitude", "longitude"]]

    return X_train_scaled, y_train, scaler
    
def get_datasets_floor_detection(df_cols, df_train):
    
    X_train_scaled, scaler = get_x_datasets(df_cols, df_train)

    # Crear las etiquetas
    y_train = df_train.drop_duplicates("id").set_index("id")["floorid"]
    
    return X_train_scaled, y_train, scaler

def train_KNN_Regressor(X_train, y_train, knn_params):
    # Configurar y entrenar modelo KNN
    knn = KNeighborsRegressor(**knn_params)
    knn.fit(X_train, y_train)
    return knn

def train_KNN_Classifier(X_train, y_train, knn_params):
    # Configurar y entrenar modelo KNN
    knn = KNeighborsClassifier(**knn_params)
    knn.fit(X_train, y_train)
    return knn
    
def save_model_to_disk(knn, scaler, df_cols, model_filename_prefix):
    # Guardar los ficheros del modelo
    joblib.dump(knn, f"./{MODELS_FOLDER}/{model_filename_prefix}_knn.pkl")
    joblib.dump(scaler, f"./{MODELS_FOLDER}/{model_filename_prefix}_scaler.pkl")
    df_cols.to_csv(f"./{MODELS_FOLDER}/{model_filename_prefix}_columns.csv", index=False, header=False)

def logging_info(msg):
    logging.info(msg)