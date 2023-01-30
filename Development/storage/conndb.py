import mysql.connector
from mysql.connector import errorcode

class Conndb:
    config = {
        'host': 'mysqldb',
        'port': 3306,
        'database': 'metricdb',
        'user': 'root',
        'password': 'root',
        'charset': 'utf8',
        'use_unicode': True,
        'get_warnings': True,
    }
    db = 0
    cursor = 0
    def __init__(self):
        try:
            self.db = mysql.connector.Connect(**self.config)
            self.cursor = self.db.cursor()
            print("Database connection established")
                 
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Error in Username or Password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)