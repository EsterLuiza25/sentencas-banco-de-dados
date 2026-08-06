import sqlite3
import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


load_dotenv()

PG_HOST = os.getenv("DB_HOST", "localhost")
PG_PORT = os.getenv("DB_PORT", "5432")
PG_DB = os.getenv("DB_NAME", "")
PG_USER = os.getenv("DB_USER", "postgres")
PG_PASSWORD = os.getenv("DB_PASSWORD", "")  

def criar_tabela_postgres(cursor_pg):
   
    print(" Criando estrutura no PostgreSQL")
    
    
    cursor_pg.execute("""
    CREATE TABLE IF NOT EXISTS sentencas (
        id SERIAL PRIMARY KEY,
        numero_processo VARCHAR(100) UNIQUE NOT NULL,
        tribunal_orgao VARCHAR(255),
        texto_sentenca_raw TEXT,
        texto_sentenca_html TEXT,
        datas_extraidas TEXT,
        termo_busca_origem VARCHAR(100)
    );
    """)
    
    
    cursor_pg.execute("""
    CREATE TABLE IF NOT EXISTS controle_fluxo (
        termo VARCHAR(100) PRIMARY KEY,
        ultima_pagina_coletada INTEGER DEFAULT 0,
        finalizado INTEGER DEFAULT 0
    );
    """)

def migrar_dados():
    
    print("📖 Lendo dados do arquivo SQLite (sentencas.db)...")
    conn_sqlite = sqlite3.connect("sentencas.db")
    cursor_sqlite = conn_sqlite.cursor()

    
    cursor_sqlite.execute("""
        SELECT numero_processo, tribunal_orgao, texto_sentenca_raw, 
               texto_sentenca_html, datas_extraidas, termo_busca_origem 
        FROM sentencas;
    """)
    sentencas = cursor_sqlite.fetchall()

    
    cursor_sqlite.execute("""
        SELECT termo, ultima_pagina_coletada, finalizado 
        FROM controle_fluxo;
    """)
    controle = cursor_sqlite.fetchall()

    print(f"Foram encontradas {len(sentencas)} sentenças no SQLite para migração.")

   
    print(" Conectando ao PostgreSQL...")
    try:
        conn_pg = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        )
        cursor_pg = conn_pg.cursor()
    except Exception as e:
        print(f" Erro ao conectar no PostgreSQL: {e}")
        return

   
    criar_tabela_postgres(cursor_pg)

    
    if sentencas:
        print(" Transferindo sentenças em lotes...")
        sql_insert_sentencas = """
        INSERT INTO sentencas (
            numero_processo, tribunal_orgao, texto_sentenca_raw, 
            texto_sentenca_html, datas_extraidas, termo_busca_origem
        ) VALUES %s
        ON CONFLICT (numero_processo) DO NOTHING;
        """
        
        execute_values(cursor_pg, sql_insert_sentencas, sentencas, page_size=1000)

    
    if controle:
        print("Transferindo histórico de controle de fluxo...")
        sql_insert_controle = """
        INSERT INTO controle_fluxo (termo, ultima_pagina_coletada, finalizado)
        VALUES %s
        ON CONFLICT (termo) DO UPDATE SET 
            ultima_pagina_coletada = EXCLUDED.ultima_pagina_coletada,
            finalizado = EXCLUDED.finalizado;
        """
        execute_values(cursor_pg, sql_insert_controle, controle)

    
    conn_pg.commit()

    print("\n MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print(f" {len(sentencas)} sentenças foram inseridas/verificadas no PostgreSQL.")

    
    cursor_sqlite.close()
    conn_sqlite.close()
    cursor_pg.close()
    conn_pg.close()

if __name__ == "__main__":
    migrar_dados()