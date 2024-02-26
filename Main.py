# main.py

import datetime
from sqlalchemy import create_engine
from WeatherDBManager import WeatherDBManager
from KMADataCollector import KMADataCollector, KMADataCollectorException
from MosquitoEstimator import MosquitoEstimator, MosquitoEstimatorException

####### 사용자 변경 부분 #######
# 현재 입력된 값은 작성자 설정값

url = 'http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList'
api_key = "UsUKNowIhuVde2uiZ8CXTqcJOuEhHcwysXCMboT9u2webjVS0kjMtEkx8j82SM0F8AsjoEAipEI3GwklijlUvA%3D%3D"
host = 'localhost'
user = 'root'
db = 'mosquito2023'
password = 'logintomysql12!'
category = ['stnNm','tm','avgTa','minTa','maxTa','sumRnDur','sumRn','avgTd','ssDur','sumGsr','avgTs','minTg']

table_name = '2023' # 내가 ASOS 데이터를 삽입할 table 이름 (사용자 임의로 설정)
json_path = 'C:/Users/psb/mosquito_db/mos/SeoulMosquito2023/coefficient2023.json'

def main():
    try:
        db_manager = WeatherDBManager(host, user, db, password)
        db_manager.get_connection()
        data_collector = KMADataCollector(url, api_key, host, user, db, password, category)
        data_collector.insert_weather_data(20230101,20231231,table_name)
        estimator = MosquitoEstimator(host, user, db, password, json_path)

        dates = [20230512, 20230622, 20230714, 20230815, 20230924, 20231022]

        for date in dates:
            print(date)
            print(f"0.지수: {estimator.get_estimated_number_of_mosquito_mean_value(0, date, table_name):.3f}")
            print(f"1.수변부: {estimator.get_estimated_number_of_mosquito_mean_value(1, date, table_name):.3f}")
            print(f"2.주거지: {estimator.get_estimated_number_of_mosquito_mean_value(2, date, table_name):.3f}")
            print(f"3.공원: {estimator.get_estimated_number_of_mosquito_mean_value(3, date, table_name):.3f}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
