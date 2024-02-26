from urllib.parse import urlencode, unquote, quote_plus
import numpy as np
import pandas as pd
import requests
import pymysql
from datetime import datetime
from sqlalchemy import create_engine
pymysql.install_as_MySQLdb()
#import MySQLdb
import mysql.connector
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pandas')

from WeatherDBManager import WeatherDBManager, WeatherDBException

class KMADataCollector:
    def __init__(self, url, api, host, user, db, password, category):
        self.url = url
        self.api = api
        self.host = host
        self.user = user
        self.db = db
        self.password = password
        self.category = category

        print(f'{self.get_table()} \nTable 별 최신 업데이트 날짜는 {self.get_latest_update_date()}')

    # API 이용하여 ASOS 데이터 받아오기 - 범위 (API 파라미터 참고하면 StartDate와 EndDate는 반드시 받아야하므로 single day를 받아오는 함수는 만들 필요X)
    def get_weather_data(self, start_date, end_date):     # date는 int type 으로 입력
        try:
            # 입력받은 date 형식이 올바른지 확인
            if len(str(start_date)) != 8:
                raise TypeError("start_date 형식에 오류가 있습니다. 날짜 형식은 YYYYMMDD 로 입력해야 합니다.")
            elif len(str(end_date)) != 8:
                raise TypeError("end_date 형식에 오류가 있습니다. 날짜 형식은 YYYYMMDD 로 입력해야 합니다.")
            elif start_date > end_date:
                raise ValueError("종료 날짜는 시작 날짜보다 빨라야 합니다.")

            start = datetime.strptime(str(start_date), '%Y%m%d')
            end = datetime.strptime(str(end_date), '%Y%m%d')
            diff = (end - start).days

            params = '?' + urlencode({quote_plus("ServiceKey"): self.api,
                                      quote_plus("numOfRows"): diff+1,  # 1 더해 줘야 end_date까지 출력됨
                                      quote_plus("dataType"): "JSON",
                                      quote_plus("dataCd"): "ASOS",
                                      quote_plus("dateCd"): "DAY",
                                      quote_plus("startDt"): str(start_date),
                                      quote_plus("endDt"): str(end_date),
                                      quote_plus("stnIds"): 108})   # 지점 : 서울(108)로 고정

            '''
            # API 요청 실패했을 때 재시도하는 과정을 for문으로
            numberOfRequest = 5
            for trial in range(1, numberOfRequest + 1):
                try:
                    obsrValue = getValueFromAPI(tag, date)
                    if obsrValue is not None:  # null값이 아니면, 한번 더 요청
                        break 
                except Exception as e:  # 예외 객체를 참조하기 위한 관례적인 변수 이름
                    try:
                        time.sleep(1)  # 평균 응답시간*0.5만큼 기다림
                    except KeyboardInterrupt:
                        raise KMADataCollectorException("인터럽트 감지됨")
            '''

            response = requests.get(self.url+unquote(params))
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()
            data_all = data['response']['body']['items']['item']
            df = pd.DataFrame.from_dict(data=data_all, orient='columns')
            return df[self.category]

        except TypeError as e1:
            print(f"Error : {e1}")
        except ValueError as e2:
            print(f"Error : {e2}")

    # 받아온 ASOS 데이터 전처리 (숫자는 모두 float type으로 변경하고 빈 곳은 nan으로 결측치 처리)
    def preprocess_weather_data(self, start_date, end_date):
        df = self.get_weather_data(start_date,end_date)
        for thing in self.category:
            try:
                df[thing] = df[thing].astype('float64')
            except:     # 날짜나 지점명 같이 float으로 변경 불가능한 column은 pass
                pass
        df.replace('',np.nan,inplace=True)      # 빈 값이 ''로 저장되어 있는 것을 nan으로 변경 (DB에 넣으면 NULL 값으로 처리됨)
        return df

    # 전처리까지 마친 ASOS 데이터 DB에 업데이트
    def insert_weather_data(self, start_date, end_date, table_name):
        w = WeatherDBManager(self.host, self.user, self.db, self.password)
        engine = w.get_connection()
        df = self.preprocess_weather_data(start_date,end_date)
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

    # DB에 있는 table 별로 업데이트 된 가장 최신 날짜 확인
    def get_latest_update_date(self):
        w = WeatherDBManager(self.host, self.user, self.db, self.password)
        connection = w.get_connection()
        table_list = self.get_table()
        date_list = []
        try:
            for table in table_list:
                query = f'SELECT * FROM {self.db}.{table}'
                df = pd.read_sql(query, connection)
                df['tm'] = pd.to_datetime(df['tm'])
                latest_date = df['tm'].max()
                try:
                    date_list.append(latest_date.strftime('%Y-%m-%d'))
                except:
                    pass
        except Exception:
            raise ValueError(f"아직 데이터가 없는 테이블이 있습니다.")
        finally:
            print(date_list)
        return date_list

    # 현재 DB에 있는 테이블 목록 보기
    def get_table(self):
        w = WeatherDBManager(self.host, self.user, self.db, self.password)
        connection = w.get_connection()
        query = f"SHOW TABLES"
        tables_df = pd.read_sql(query, connection)
        tables = tables_df[tables_df.columns[0]]
        return tables

class KMADataCollectorException(Exception):
    def __init__(self, error_msg):
        super().__init__(error_msg)

