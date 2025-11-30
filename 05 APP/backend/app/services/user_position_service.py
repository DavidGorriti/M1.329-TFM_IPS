from repositories.database_repo import Database

class UserPositionService:

    def __init__(self):
        # Inicializa Database
        self.db = Database()

    def get_users_positions(self):
        # Llamada a Database.get_users_positions()
        return self.db.get_users_positions()
        
    def update_user_info(self,data,wifi_measurements):
        # Llamada a Database.update_user_info()
        self.db.update_user_info(data,wifi_measurements)
        
    def clear_users_positions(self):
        # Llamada a Database.clear_users_positions()
        self.db.clear_users_positions()
        