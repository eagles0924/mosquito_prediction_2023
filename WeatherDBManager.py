import pymysql

class WeatherDBManager:
    def __init__(self, host, user, password, database):
        try:
            self.connection = pymysql.connect(host=host, user=user, password=password, database=database)
            self.cursor = self.connection.cursor()
        except Exception as e:
            raise WeatherDBException(f"DB 연결 실패: {e}")

    def perform_sql(self, sql):
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as e:
            raise WeatherDBException(f"SQL 실행 실패: {e}")

    def perform_sql_update(self, sql):
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except Exception as e:
            raise WeatherDBException(f"SQL 업데이트 실패: {e}")

    def close_connection(self):
        self.connection.close()
