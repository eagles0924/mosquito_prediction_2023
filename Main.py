# main.py

import datetime
from WeatherDBManager import WeatherDBManager
from KMADataCollector import KMADataCollector, KMADataCollectorException
from MosquitoEstimator import MosquitoEstimator, MosquitoEstimatorException

def main():
    try:
        db_manager = WeatherDBManager(host="localhost", user="root", password="password", database="mosquito")
        api_key = "pXXaeWEIuVdjMlCgkw0hRD7AXDMNsj4bYMlkSdIFEARjBof45ziaPljeSzVGjwZ2"
        data_collector = KMADataCollector(api_key)
        important_keys = ["SS_DUR", "MIN_TG", "MIN_TA", "SUM_RN_DUR", "MAX_WS", "SUM_GSR", "MAX_TA", "AVG_RHM", "MIN_RHM", "AVG_TD", "AVG_TA", "AVG_WS"]
        estimator = MosquitoEstimator(db_manager, data_collector)

        dates = ["20220501", "20220530", "20220615", "20221023"]

        for key in important_keys:
            print(f"Key = {key}")
            data_collector.insert_weather_data(key, "20220430", "20221115")

        for date in dates:
            print(date)
            print(f"지수: {estimator.get_estimated_number_of_mosquito_mean_value(0, date):.3f}")
            print(f"1.수변부: {estimator.get_estimated_number_of_mosquito_mean_value(1, date):.3f}")
            print(f"2.주거지: {estimator.get_estimated_number_of_mosquito_mean_value(2, date):.3f}")
            print(f"3.공원: {estimator.get_estimated_number_of_mosquito_mean_value(3, date):.3f}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
