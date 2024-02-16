# mysql host

import pymysql

def get_connection(host, user, db, pw):
    connection = pymysql.connect(
        host=host,
        user=user,
        database=db,
        password=pw,
        charset='utf8')

    return connection

get_connection('localhost','root','mosquito','logintomysql12!')
