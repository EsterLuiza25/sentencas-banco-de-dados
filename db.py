import sqlite3

ARQUIVO_BANCO = "sentencas.db"

def conectar():
    return sqlite3.connect(ARQUIVO_BANCO)


def criar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sentencas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_processo TEXT UNIQUE NOT NULL,
            assuntos TEXT,
            tribunal_orgao TEXT,
            classe_processual TEXT,
            data_juntada TEXT,
            texto_sentenca_raw TEXT,
            texto_sentenca_html TEXT,
            datas_extraidas TEXT,
            termo_busca_origem TEXT,
            data_coleta TEXT,
            hash_conteudo TEXT,
            url_origem TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progresso (
            termo TEXT PRIMARY KEY,
            cursor TEXT,
            finalizado INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS controle_fluxo (
            termo TEXT PRIMARY KEY,
            ultima_pagina_coletada INTEGER DEFAULT 0,
            search_after_value TEXT,
            finalizado INTEGER DEFAULT 0
        )
    """)

    conexao.commit()
    conexao.close()


def buscar_progresso(termo):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT cursor, finalizado FROM progresso WHERE termo = ?", (termo,))
    resultado = cursor.fetchone()

    conexao.close()

    if not resultado:
        return None, False

    cursor_salvo, finalizado = resultado
    return cursor_salvo, bool(finalizado)


def salvar_progresso(termo, cursor_atual, finalizado=False):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO progresso (termo, cursor, finalizado)
        VALUES (?, ?, ?)
        ON CONFLICT(termo) DO UPDATE SET
            cursor = excluded.cursor,
            finalizado = excluded.finalizado
    """, (termo, cursor_atual, 1 if finalizado else 0))

    conexao.commit()
    conexao.close()


def salvar_sentenca(dados):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO sentencas (
            numero_processo,
            assuntos,
            tribunal_orgao,
            classe_processual,
            data_juntada,
            texto_sentenca_raw,
            texto_sentenca_html,
            datas_extraidas,
            termo_busca_origem,
            data_coleta,
            hash_conteudo,
            url_origem
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(numero_processo) DO UPDATE SET
            assuntos = excluded.assuntos,
            tribunal_orgao = excluded.tribunal_orgao,
            classe_processual = excluded.classe_processual,
            data_juntada = excluded.data_juntada,
            texto_sentenca_raw = excluded.texto_sentenca_raw,
            texto_sentenca_html = excluded.texto_sentenca_html,
            datas_extraidas = excluded.datas_extraidas,
            termo_busca_origem = excluded.termo_busca_origem,
            data_coleta = excluded.data_coleta,
            hash_conteudo = excluded.hash_conteudo,
            url_origem = excluded.url_origem
    """, (
        dados.get("numero_processo"),
        dados.get("assuntos"),
        dados.get("tribunal_orgao"),
        dados.get("classe_processual"),
        dados.get("data_juntada"),
        dados.get("texto_sentenca_raw"),
        dados.get("texto_sentenca_html"),
        dados.get("datas_extraidas"),
        dados.get("termo_busca_origem"),
        dados.get("data_coleta"),
        dados.get("hash_conteudo"),
        dados.get("url_origem"),
    ))

    conexao.commit()
    conexao.close()