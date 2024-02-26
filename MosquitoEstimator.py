# 일단은 python에서 계산 후 db에 넣는 과정

import numpy as np
import pandas as pd
import json
from datetime import datetime
from sqlalchemy import create_engine
from WeatherDBManager import WeatherDBManager,WeatherDBException
from datetime import timedelta

class MosquitoEstimator:
    def __init__(self, host, user, db, password, json_path):
        self.host = host
        self.user = user
        self.db = db
        self.password = password
        self.json_path = json_path

    # 2023년 버전 coefficient가 저장된 json 파일 읽어오기 (데이터는 dictionary 구조)
    def read_coefficient(self):
        co2023 = self.json_path
        with open(co2023, 'r') as file:
            co2023_data = json.load(file)
        return co2023_data

    def get_estimated_number_of_mosquito_mean_value(self, area_type, date, table_name):
        w = WeatherDBManager(self.host, self.user, self.db, self.password)
        engine = w.get_connection()
        date_use = datetime.strptime(str(date), '%Y%m%d') - timedelta(days=1)  # 예측할 날짜를 입력한 것이기 때문에 하루 전날의 데이터를 이용
        date_dash = date_use.strftime('%Y-%m-%d')
        query = f'SELECT * FROM {self.db}.{table_name}'

        df = pd.read_sql(query, engine)
        df_target = df[df['tm'] == date_dash]

        # 예측값 초기화
        predval = 0.0

        co2023_data = self.read_coefficient()
        params = co2023_data[str(area_type)][str(date_use.month)]
        params_list = list(params.keys())
        try:
            for i, key in enumerate(params_list):
                if i == 0:
                    predval += params[params_list[i]]
                elif pd.notna(df_target[key].iloc[0]):
                    try:    # 계산식에 포함된 데이터가 결측값인 경우 무시하고 진행할지, 해당 달의 평균값으로 대체할지 질문
                        predval += df_target[key].iloc[0] * params[params_list[i]]
                    except:
                        pass
        except Exception:
            raise MosquitoEstimatorException(f"모기 예측에 실패하였습니다. area_type과 date를 바르게 입력하였는지 확인하세요.")
        if predval < 0:
            return 0
        else:
            return predval

    def connect(self):
        try:
            db_connection_str = "mysql+mysqldb://" + self.user + ":" + self.password + "@" + self.host + "/" + self.db
            db_connection = create_engine(db_connection_str, encoding='utf-8')
        except Exception:
            raise WeatherDBException(f"DB 연결에 실패했습니다. host, user, password 혹은 db 이름을 다시 확인해주세요.")
        return db_connection


class MosquitoEstimatorException(Exception):
    def __init__(self, error_msg, err=None):
        super().__init__(error_msg, err)