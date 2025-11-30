import psycopg
import logging
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.model_selection import train_test_split


# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("Training.log"),
        logging.StreamHandler()
    ]
)

KNN_PARAMS = {
        'n_neighbors': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17],
        'metric': ['euclidean', 'manhattan', 'chebyshev', 'minkowski'],
        'p': [1, 2]
    }
    

def get_connection():
    return psycopg.connect(
        dbname="postgres",
        user="postgres",
        password="admin",
        host="localhost",
        port="5432"
    )

def mean_absolute_error(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    distances = np.sqrt(np.sum((y_true - y_pred)**2, axis=1))
    return np.mean(distances)
    
def root_mean_squared_error(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    return np.sqrt(np.mean((y_true - y_pred)**2))
    

def train_2d_model(sql_columns, sql_training, sql_testing):
    df_cols = read_sql(sql_columns)
    df_train = read_sql(sql_training)
    df_test = read_sql(sql_testing)

    X_train_scaled, y_train, X_test_scaled, y_test = get_datasets_2d(df_cols, df_train, df_test)

    logging_info(f"X_train_scaled shape: {X_train_scaled.shape}")
    logging_info(f"y_train shape: {y_train.shape}")
    logging_info(f"X_test_scaled shape: {X_test_scaled.shape}")
    logging_info(f"y_test shape: {y_test.shape}")

    # Configurar y entrenar modelo KNN
    train_KNN_Regressor(X_train_scaled, y_train, X_test_scaled, y_test)
    
def train_floor_detection_model(sql_columns, sql_training, sql_testing):
    df_cols = read_sql(sql_columns)
    df_train = read_sql(sql_training)
    df_test = read_sql(sql_testing)

    X_train_scaled, y_train, X_test_scaled, y_test = get_datasets_floor_detection(df_cols, df_train, df_test)

    logging_info(f"X_train_scaled shape: {X_train_scaled.shape}")
    logging_info(f"y_train shape: {y_train.shape}")
    logging_info(f"X_test_scaled shape: {X_test_scaled.shape}")
    logging_info(f"y_test shape: {y_test.shape}")

    # Configurar y entrenar modelo KNN
    train_KNN_Classifier(X_train_scaled, y_train, X_test_scaled, y_test)

def train_2d_model_80_20(sql_columns, sql_train):
    df_cols = read_sql(sql_columns)
    df_train = read_sql(sql_train)

    X = df_train.pivot_table(
        index="id",
        columns="mac_bssid",
        values="rss",
        fill_value=-120
    )
    
    # Alinear columnas para asegurar que no falten columnas
    X = X.reindex(columns=df_cols["mac_bssid"].tolist(), fill_value=-120)
    
    # Crear las etiquetas
    y = df_train.drop_duplicates("id").set_index("id")[["projectedx", "projectedy"]]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, shuffle=True, random_state=42
    )
    
    X_train_scaled, X_test_scaled = get_x_scaled(X_train, X_test)

    logging_info(f"X_train_scaled shape: {X_train_scaled.shape}")
    logging_info(f"y_train shape: {y_train.shape}")
    logging_info(f"X_test_scaled shape: {X_test_scaled.shape}")
    logging_info(f"y_test shape: {y_test.shape}")

    # Configurar y entrenar modelo KNN
    train_KNN_Regressor(X_train_scaled, y_train, X_test_scaled, y_test)
    
def train_floor_detection_model_80_20(sql_columns, sql_train):
    df_cols = read_sql(sql_columns)
    df_train = read_sql(sql_train)

    X = df_train.pivot_table(
        index="id",
        columns="mac_bssid",
        values="rss",
        fill_value=-120
    )
    
    # Alinear columnas para asegurar que no falten columnas
    X = X.reindex(columns=df_cols["mac_bssid"].tolist(), fill_value=-120)
    
    # Crear las etiquetas
    y = df_train.drop_duplicates("id").set_index("id")["floorid"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, shuffle=True, random_state=42
    )
    
    X_train_scaled, X_test_scaled = get_x_scaled(X_train, X_test)

    logging_info(f"X_train_scaled shape: {X_train_scaled.shape}")
    logging_info(f"y_train shape: {y_train.shape}")
    logging_info(f"X_test_scaled shape: {X_test_scaled.shape}")
    logging_info(f"y_test shape: {y_test.shape}")

    # Configurar y entrenar modelo KNN
    train_KNN_Classifier(X_train_scaled, y_train, X_test_scaled, y_test)

def read_sql(sql):
    conn = get_connection()
    df = pd.read_sql(sql, conn)
    conn.close()
    return df

def get_x_scaled(X_train, X_test):
    # Escalar los valores
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)
    
    return X_train_scaled, X_test_scaled

def get_x_datasets(df_cols, df_train, df_test):
    # Pivotar el conjunto de tablas. Cada fila son las coordenadas y cada columna un punto de acceso. Los valores son el RSSI
    X_train = df_train.pivot_table(
        index="id",
        columns="mac_bssid",
        values="rss",
        fill_value=-120
    )
    X_test = df_test.pivot_table(
        index="id",
        columns="mac_bssid",
        values="rss",
        fill_value=-120
    )

    # Alinear columnas para asegurar que no falten columnas
    X_train = X_train.reindex(columns=df_cols["mac_bssid"].tolist(), fill_value=-120)
    X_test = X_test.reindex(columns=X_train.columns, fill_value=-120)
    
    # Escalar los valores
    X_train_scaled, X_test_scaled = get_x_scaled(X_train, X_test)
    
    return X_train_scaled, X_test_scaled

def get_datasets_2d(df_cols, df_train, df_test):

    X_train_scaled, X_test_scaled = get_x_datasets(df_cols, df_train, df_test)
    
    # Crear las etiquetas
    y_train = df_train.drop_duplicates("id").set_index("id")[["projectedx", "projectedy"]]
    y_test = df_test.drop_duplicates("id").set_index("id")[["projectedx", "projectedy"]]

    
    return X_train_scaled, y_train, X_test_scaled, y_test
    
def get_datasets_floor_detection(df_cols, df_train, df_test):
    
    X_train_scaled, X_test_scaled = get_x_datasets(df_cols, df_train, df_test)

    # Crear las etiquetas
    y_train = df_train.drop_duplicates("id").set_index("id")["floorid"]
    y_test = df_test.drop_duplicates("id").set_index("id")["floorid"]

    
    return X_train_scaled, y_train, X_test_scaled, y_test

def get_grid_search_cv(knn, X_train, y_train, scoring):
    grid = GridSearchCV(knn, KNN_PARAMS, scoring=scoring, n_jobs=-1)
    grid.fit(X_train, y_train)
    return grid

def train_KNN_Regressor(X_train, y_train, X_test, y_test):
    # Configurar y entrenar modelo KNN
    knn = KNeighborsRegressor()
    
    grid = get_grid_search_cv(knn, X_train, y_train, 'neg_mean_squared_error')

    # Mejor modelo
    best_knn = grid.best_estimator_
    y_pred = best_knn.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)
    
    logging_info(f"Best combination: {grid.best_params_}")
    logging_info(f"MAE: {mae} metros")
    logging_info(f"RMSE: {rmse} metros")

def train_KNN_Classifier(X_train, y_train, X_test, y_test):
    # Configurar y entrenar modelo KNN
    knn = KNeighborsClassifier()

    grid = get_grid_search_cv(knn, X_train, y_train, 'accuracy')

    # Mejor modelo
    best_knn = grid.best_estimator_
    y_pred = best_knn.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    logging_info(f"y_test: {y_test.to_numpy()}")
    logging_info(f"y_pred: {y_pred}")

    logging_info(f"Best combination: {grid.best_params_}")
    logging_info(f"Accuracy: {round(accuracy*100, 2)}%")  

def logging_info(msg):
    logging.info(msg)