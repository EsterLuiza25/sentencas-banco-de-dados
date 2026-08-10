import json
import time
import client
import db
import parser


TERMOS = [
    "Crimes Militares",
    "Deserção",
    "Insubmissão",
    "Abandono de Posto",
    "Insubordinação",
    "Furto Militar",
    "Peculato",
    "Estelionato",
    "Falsificação de Documento",
    "Descumprimento de Missão",
    "Violência Contra Superior",
    "Violência Contra Inferior",
    "Dormir em Serviço",
    "Embriaguez em Serviço",
    "Abuso de Autoridade",
    "Tráfico de Drogas",
    "Homicídio",
    "Lesão Corporal",
    "Recusa de Obediência",
    "Extravio de Material Militar",
]

TAMANHO_LOTE = 20
PAUSA_SEGUNDOS = 1


def preparar_sentenca(item, termo):
    texto = item.get("texto", "")

    return {
        "numero_processo": item.get("num_processo"),
        "assuntos": json.dumps(item.get("des_assuntos", []), ensure_ascii=False),
        "tribunal_orgao": item.get("des_orgao"),
        "classe_processual": item.get("des_classe"),
        "data_juntada": item.get("data_juntada"),
        "texto_sentenca_raw": texto,
        "texto_sentenca_html": parser.transformar_em_html(texto),
        "datas_extraidas": parser.achar_datas(texto),
        "termo_busca_origem": termo,
        "data_coleta": parser.obter_data_coleta(),
        "hash_conteudo": parser.gerar_hash(texto),
        "url_origem": item.get("url", "")
    }


def coletar_termo(termo):
    cursor, finalizado = db.buscar_progresso(termo)

    if finalizado:
        print(f"Termo ja concluido: {termo}")
        return

    pagina = 1

    while True:
        print(f"Buscando {termo} - pagina {pagina}")

        resposta = client.buscar_sentencas(termo, TAMANHO_LOTE, cursor)
        sentencas = resposta.get("sentencas", [])
        total = resposta.get("total", 0)

        if not sentencas:
            db.salvar_progresso(termo, cursor, finalizado=True)
            print(f"Fim do termo: {termo}")
            return

        for item in sentencas:
            dados = preparar_sentenca(item, termo)

            if dados["numero_processo"]:
                db.salvar_sentenca(dados)

        cursor = sentencas[-1].get("@timestamp")
        db.salvar_progresso(termo, cursor, finalizado=False)

        print(f"Salvas {len(sentencas)} sentencas. Total informado pela API: {total}")

        if len(sentencas) < TAMANHO_LOTE:
            db.salvar_progresso(termo, cursor, finalizado=True)
            print(f"Fim do termo: {termo}")
            return

        pagina += 1
        time.sleep(PAUSA_SEGUNDOS)


def main():
    db.criar_banco()
    print("Coleta iniciada.")

    for termo in TERMOS:
        coletar_termo(termo)

    print("Coleta finalizada.")


if __name__ == "__main__":
    main()