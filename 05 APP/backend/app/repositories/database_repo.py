import psycopg
import json
import pandas as pd
from zoneinfo import ZoneInfo
from typing import List
from models.user import User
from config.config import Config

class Database:
    
    config = Config()
    
    CURRENT_TIMEZONE = ZoneInfo(config.timezone)
    
    GET_USER = """
        SELECT id FROM tfm_ips.user
        WHERE devicename = %s
    """
    
    UPDATE_USER = """
        INSERT INTO tfm_ips.user (devicename)
        VALUES (%s) RETURNING id;
    """
    
    UPDATE_USER_POSITION = """
        INSERT INTO tfm_ips.userposition(
        userid, systemtimestamp, latitude, longitude, floorid)
        VALUES (%s, %s, %s, %s, %s);
    """
    
    UPDATE_USER_WIFI = """
        INSERT INTO tfm_ips.userwifi(
        userid, systemtimestamp, mac_bssid, rss)
        VALUES (%s, %s, %s, %s);
    """
    
    GET_USERS_POSITIONS_QUERY = """
        SELECT DISTINCT ON (userid)
            up.id as id,
			u.devicename as devicename,
            userid,
            systemtimestamp,
            latitude,
            longitude,
            floorid
        FROM tfm_ips.userposition up
		join tfm_ips.user u on up.userid = u.id
        ORDER BY userid, systemtimestamp DESC;
    """

    DELETE_USERS = """
        DELETE FROM tfm_ips.user;
    """
    
    def __init__(self):
        db_conf = self.config.database

        # Guardar parámetros de conexión como atributo de instancia
        self.conn_params = {
            "dbname": db_conf["dbname"],
            "user": db_conf["user"],
            "password": db_conf["password"],
            "host": db_conf["host"],
            "port": db_conf["port"]
        }

    def get_connection(self):
        # Devuelve una conexión nueva a PostgreSQL usando psycopg.
        return psycopg.connect(**self.conn_params)

    def get_users_positions(self) -> List[User]:
        #Devuelve un DataFrame con las posiciones actuales de personas.
        with self.get_connection() as conn:
            df = pd.read_sql(self.GET_USERS_POSITIONS_QUERY, conn)
        
        users = [
            User(
                id=row["id"],
                userId=row["userid"],
                deviceName=row["devicename"],
                lastUpdateTimestamp=row["systemtimestamp"].replace(tzinfo=ZoneInfo("UTC")).astimezone(self.CURRENT_TIMEZONE),
                latitude=row["latitude"],
                longitude=row["longitude"],
                floorId=row["floorid"],
                lastUpdateInSeconds=-1
            )
            for _, row in df.iterrows()
        ]

        return users
        
    def update_user_info(self, position, wifi_measurements):
        # Actualiza la información de la base de datos online de la persona
        try:
            conn = self.get_connection()
            
            with conn.cursor() as cur:
                # Obtiene o inserta la persona usuaria
                cur.execute(self.GET_USER, (position["device_name"],))
                row = cur.fetchone()
                if row is not None:
                    user_id = row[0]
                else:
                    cur.execute(self.UPDATE_USER, (position["device_name"],))
                    user_id = cur.fetchone()[0]

                # Actualiza su posición
                cur.execute(self.UPDATE_USER_POSITION, (user_id,position["currentTimestamp"],position["latitude"],position["longitude"],position["floorId"],))
                
                # Actualiza sus mediciones WIFI
                wifi_records = [
                        (user_id, position["currentTimestamp"], measurement.mac_bssid, measurement.rssi)
                        for measurement in wifi_measurements
                    ]
                cur.executemany(self.UPDATE_USER_WIFI, wifi_records)
            
            conn.commit()
            
        except Exception as e:
            print(e)
            conn.rollback()
        finally:
            conn.close()

    def clear_users_positions(self):
        # Borra los datos la base de datos de ubicaciones online
        try:
            conn = self.get_connection()
            
            with conn.cursor() as cur:
                cur.execute(self.DELETE_USERS)
            
            conn.commit()
            
        except Exception as e:
            print(e)
            conn.rollback()
        finally:
            conn.close()
