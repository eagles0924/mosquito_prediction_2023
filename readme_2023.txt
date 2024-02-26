SeoulMosquito2023 사용법 (ver. Python)

========= 중요!!! ==========

2023년 모기예보제 운영 지침에 따라 모기지수 산출에 쓰이는 모든 기상청 ASOS 데이터는 "하루 전날"의 수치를 넣어 주어야 합니다.

 - ASOS 데이터는 항상 "실측치" 이므로, 가장 최신의 데이터는 쿼리 당일 기준 전날의 수치입니다.
 - 따라서 쿼리 당일날의 모기지수를 산출하기 위해서는 가장 최신의 데이터를 쓰시면 됩니다.

ex) 모기지수를 업데이트하고자 하는 날, 즉 오늘이 2024년 5월 2일이라고 가정한다면, 
    MosquitoEstimator에 가장 최신 데이터인 20240502을 입력하시면 됩니다.
    5월 2일 당일에는 아직 "실측치"가 올라오지 않은 시점이므로, 5월 1일이 ASOS 데이터 중 가장 최신 데이터입니다.

KMADataCollector에서 get_weather_data() 혹은 insert_weather_data를 사용하실 때 한 번에 1000일을 초과하는 기간을 입력하면 오류가 발생합니다. (한 번에 최대 1000일 데이터 호출 가능)

또한 insert_weather_data를 통해 DB에 데이터를 저장하실 경우, 연도별로 table을 만들어 저장하시는 것을 추천합니다. (작성자의 경우 2023년 데이터는 `2023` 이름의 table에 저장함)

========================
0-0. Python 구동 시, 필요한 라이브러리 설치를 위해 requirements.txt 파일에 저장된 라이브러리를 설치해주도록 합니다.
파이썬 프로그램의 터미널에서 pip install -r requirements.txt    명령어를 입력하면 파일 안에 있는 라이브러리가 모두 설치됩니다.

0-1. MySQL 설치 및 서버와의 연결은 (host, user명 및 password 설정) 다음 링크를 참고하세요.

https://shinysblog.tistory.com/20

MySQL 설치를 마치고 설정까지 완료한 후, MySQL Connection에 생성된 사용자에 들어간 후, CREATE DATABASE mosquito2023;  명령문을 이용하여 schema(DB) 생성 후 다음을 진행한다.
*** 데이터베이스명 mosquito2023은 작성자 설정이므로 사용자 편의에 맞게 바꾸어도 됨.

1. 2020년, 2021년과 달리 변수의 수가 많아진 산식에 따라, 쿼리의 계수(coefficients)를 코드 내에 저장하기보단, coefficients.json 파일에 따로 저장
   혹시 오타 등으로 이상적인 수치가 발견된다면, coefficient2023.json 파일을 수정해주시면 됩니다.


2. 사용되는 ASOS 데이터(변수)는 다음과 같습니다. Main.py의 category 리스트와 동일합니다.

(constant)      	상수
avgTa 		평균기온
minTa 		최저기온
maxTa		최고기온
sumRnDur		강수 계속시간
sumRn		일 강수량
avgTd		평균 이슬점온도
ssDur			가조시간
sumGsr		합계 일사량
avgTs			평균 지면온도
minTg		최저 초상온도

(2022와 비교하여 습도, 풍속 삭제)


3. WeatherDBManager
 - 생성자 파라미터 (host, user, db, password)
	host : MySQL에서 host 이름 (대부분 localhost 또는 127.0.0.1로 설정됨)
	user : MySQL에서 user 이름 (대부분 root로 설정되나 변경할 수 있음)
	db : MySQL에서 schema(DB)명 (생성 시 사용자 임의로 설정. 제작자는 mosquito2023으로 설정함)
	password : MySQL에서 new connection 생성 시 설정하고 추후에 접속 시 사용하는 암호 (생성 시 사용자 임의로 설정. 제작자는 logintomysql12!로 설정)

 - 용도: MySQL DB에 접속 및 연결 유무 확인


4. KMADataCollector (기상청 ASOS 데이터를 호출 및 DB에 저장)
 - 생성자 파라미터 (url, api, host, user, db, password, category)
	url : http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList ('종관ASOS_일자료_조회서비스_오픈API활용가이드' 파일의 p.8 요청메세지 링크 첫줄)
	api : 일반 인증기 (Encoding) - 환경이나 호출 조건에 따라 Decoding 일 수도 있음
	host : MySQL에서 host 이름 (대부분 localhost 또는 127.0.0.1로 설정됨)
	user : MySQL에서 user 이름 (대부분 root로 설정되나 변경할 수 있음)
	db : MySQL에서 schema(DB)명 (생성 시 사용자 임의로 설정. 제작자는 mosquito2023으로 설정함)
	password : MySQL에서 new connection 생성 시 설정하고 추후에 접속 시 사용하는 암호 (생성 시 사용자 임의로 설정. 제작자는 logintomysql12!로 설정)

url과 api의 경우 https://www.data.go.kr/에서 ASOS 일 단위 자료에 서비스 신청을 하여 개인적으로 얻을 수 있습니다.

현재 ASOS API가 개편되어 기존에 사용하던 "https://data.kma.go.kr"로 시작하는 링크는 사용 불가능하며, "http://apis.data.go.kr"로 시작하는 링크여야 함.

- get_weather_data
	start_date : 데이터 수집을 시작할 날짜
	end_date : 데이터 수집을 마칠 날짜

- insert_weather_data
	star_date : DB에 데이터 삽입을 시작할 날짜
	end_date : DB에 데이터 삽입을 마칠 날짜
	table_name : 삽입할 데이터의 table 이름 설정 (사용자 설정)



5.  MosquitoEstimator
 - 생성자 파라미터(host, user, db, password, json_path)
	host : MySQL에서 host 이름 (대부분 localhost 또는 127.0.0.1로 설정됨)
	user : MySQL에서 user 이름 (대부분 root로 설정되나 변경할 수 있음)
	db : MySQL에서 schema(DB)명 (생성 시 사용자 임의로 설정. 제작자는 mosquito2023으로 설정함)
	password : MySQL에서 new connection 생성 시 설정하고 추후에 접속 시 사용하는 암호 (생성 시 사용자 임의로 설정. 제작자는 logintomysql12!로 설정)
	json_path : coefficient2023.json 파일이 위치한 절대 경로


---------------------------모기예측 실행------------------------------

WeatherDBManager.py, KMADataCollector.py, MosquitoEstimator.py, Main.py, coefficient2023.json 파일을 모두 같은 경로에 위치하도록 한다.

WeatherDBManager.py, KMADataCollector.py, MosquitoEstimator.py 을 각각 Run 한다.

Main.py에서 사용자 변경 부분인 url, api_key, host, user, db, password, category, table_name, json_path를 모두 사용자의 환경에 맞게 수정한 후 Run 한다.


*__pycache__ 폴더는 신경쓰지 않으셔도 됩니다.

*문의사항은 이메일(eagles0924@gmail.com)을 통해 저에게 직접 보내주시면 감사하겠습니다.