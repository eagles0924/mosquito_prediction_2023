from urllib.parse import urlencode, unquote, quote_plus
import pandas as pd
import requests
import pymysql
from datetime import datetime
from host_call import get_connection

from sqlalchemy import create_engine
pymysql.install_as_MySQLdb()
import MySQLdb

class KMADataCollector:
    # category는 list type, 나머지는 ' '을 포함한 str type으로 입력.
    def __init__(self, url, api, host, user, db, password, category):
        self.url = url
        self.api = api
        self.host = host
        self.user = user
        self.db = db
        self.password = password
        self.category = category

    def get_weather_data(self, start_date, end_date):     # date는 int type 으로 입력
        try:
            # url 및 key는 개별 사용자화
            #url = 'http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList'
            #key = "UsUKNowIhuVde2uiZ8CXTqcJOuEhHcwysXCMboT9u2webjVS0kjMtEkx8j82SM0F8AsjoEAipEI3GwklijlUvA%3D%3D"

            start = datetime.strptime(str(start_date), '%Y%m%d')
            end = datetime.strptime(str(end_date), '%Y%m%d')
            diff = (end - start).days

            params = '?' + urlencode({quote_plus("ServiceKey"): self.api,
#                                      quote_plus("pageNo"): 1,
                                      quote_plus("numOfRows"): diff+1,  # 1 더해줘야 마지막 날짜가 잘리지 않음
                                      quote_plus("dataType"): "JSON",
                                      quote_plus("dataCd"): "ASOS",
                                      quote_plus("dateCd"): "DAY",
                                      quote_plus("startDt"): str(start_date),
                                      quote_plus("endDt"): str(end_date),
                                      quote_plus("stnIds"): 108})   # 지점 : 서울(108)
            response = requests.get(self.url+unquote(params))
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()
            data_all = data['response']['body']['items']['item']
            df = pd.DataFrame.from_dict(data=data_all, orient='columns')

            return df[self.category]

        except Exception as e:
            #raise KMADataCollectorException(f"날씨 데이터 수집 실패: {e}")
            raise print(f"날씨 데이터 수집 실패: {e}")

    def preprocess_weather_data(self, start_date, end_date):
        df = self.get_weather_data(start_date,end_date)
        for thing in self.category:
            try:
                df[thing] = df[thing].astype('float64')
            except:
                pass
        return df

    def insert_weather_data(self, start_date, end_date, name):  # sql db에 테이블 생성 시 name 정해주기
        try:
            weather_data = self.get_weather_data(start_date, end_date)
            # Insert the data into your MySQL database
            db_connection_str = "mysql+mysqldb://root:"+"logintomysql12!"+"@localhost/mosquito" # "mysql+mysqldb://root:"+"password"+"@localhost/db_name" 형식으로 저장
            db_connection = create_engine(db_connection_str, encoding='utf-8')
            conn = db_connection.connect()
            df = self.preprocess_weather_data(start_date,end_date)

            dtypesql = {']'
            }
            df.to_sql(name=name, con=db_connection, if_exists='append', index=False)

        except Exception as e:
            raise print(f"날씨 데이터 삽입 실패: {e}")

    # 입력 받은 날짜가 형식(YYYYMMDD)에 맞는지 확인
    def is_date_format(self, date):
        if len(date) != 8:
            return False
        for char in date:
            if not char.isdigit():
                return False
        return True

class KMADataCollectorException(Exception):
    def __init__(self, error_msg, err=None):
        super().__init__(error_msg, err)

