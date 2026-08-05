import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.getenv("DB_HOST", "")
PG_PORT = os.getenv("DB_PORT", "")
PG_DB = os.getenv("DB_NAME", "")
PG_USER = os.getenv("DB_USER", "")
PG_PASSWORD = os.getenv("DB_PASSWORD", "")

try:
    conexao = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )
    print("Conexão realizada com sucesso!")
    conexao.close()
except Exception as error:
    print(f"Erro ao conectar: {error}")