import pymysql
from sqlalchemy import create_engine

class WeatherDBManager:
    def __init__(self, host, user, db, password):
        self.host = host
        self.user = user
        self.db = db
        self.password = password
    def get_connection(self):
        self.db_connection_str = "mysql+mysqldb://" + self.user + ":" + self.password + "@" + self.host + "/" + self.db
        self.db_connection = create_engine(self.db_connection_str+ '?charset=utf8mb4')
        try:
            connection = self.db_connection.connect()
        except Exception:
            raise WeatherDBException(f"DB 연결에 실패했습니다. host, user, password 혹은 db 이름을 다시 확인 해주세요.")
        return self.db_connection

class WeatherDBException(Exception):
    def __init__(self, error_msg, err=None):
        super().__init__(error_msg, err)
