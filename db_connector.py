import mysql.connector

def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd=""
    )