import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Carrega variáveis do .env
load_dotenv()


def get_db_connection():
    """
    Cria e retorna uma conexão com o banco MariaDB.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv('SERVICE_NAME'),
            database=os.getenv('DATABASE_NAME'),
            user=os.getenv('MARIADB_USER'),
            password=os.getenv('MARIADB_PASSWORD'),
            port=os.getenv('DATABASE_PORT')
        )
        
        if connection.is_connected():
            return connection
            
    except Error as e:
        print(f"Erro ao conectar ao MariaDB: {e}")
        raise


def get_db_cursor(connection):
    """
    Retorna um cursor da conexão fornecida.
    """
    return connection.cursor()


def close_db_connection(connection, cursor=None):
    """
    Fecha cursor e conexão com o banco.
    """
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()
