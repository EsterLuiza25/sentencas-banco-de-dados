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
    "Motim",
    "Revolta",
    "Prevaricação",
    "Concussão",
    "Corrupção Passiva",
    "Uso Indevido de Uniforme",
    "Dano em Material Bélico",
    "Desrespeito a Superior",
    "Ofensa Aviltante a Inferior",
    "Porte Ilegal de Arma de Fogo",
]

TAMANHO_LOTE = 20
PAUSA_SEGUNDOS = 1
MAX_PAGINAS_SEM_NOVIDADE = 3


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


def sincronizar_diariamente(termo):
    cursor = None
    pagina = 1
    paginas_sem_novidade = 0
    total_novos_termo = 0

    print(f"\n--- Sincronizando Termo: '{termo}' ---")

    while True:
        resposta = client.buscar_sentencas(termo, TAMANHO_LOTE, cursor)
        sentencas = resposta.get("sentencas", [])
        total_api = resposta.get("total", 0)

        if not sentencas:
            print(f"[{termo}] Sem mais registros retornados pela API.")
            break

        novos_nesta_pagina = 0
        for item in sentencas:
            dados = preparar_sentenca(item, termo)
            if dados["numero_processo"]:
                if db.salvar_sentenca(dados):
                    novos_nesta_pagina += 1

        total_novos_termo += novos_nesta_pagina
        print(f"[{termo}] Pág {pagina}: {len(sentencas)} avaliadas | {novos_nesta_pagina} inseridas/atualizadas (Total na base do tribunal: {total_api})")

        if novos_nesta_pagina == 0:
            paginas_sem_novidade += 1
        else:
            paginas_sem_novidade = 0  

        if paginas_sem_novidade >= MAX_PAGINAS_SEM_NOVIDADE:
            print(f"[{termo}] {MAX_PAGINAS_SEM_NOVIDADE} páginas consecutivas sem novidades. Termo totalmente sincronizado.")
            break

        cursor = sentencas[-1].get("@timestamp")

        if len(sentencas) < TAMANHO_LOTE:
            print(f"[{termo}] Fim do catálogo na API.")
            break

        pagina += 1
        time.sleep(PAUSA_SEGUNDOS)

    print(f"Resultado para '{termo}': {total_novos_termo} alterações/novidades salvas.")


def main():
    db.criar_banco()
    print("=====================================================")
    print("  INICIANDO ATUALIZAÇÃO DIÁRIA DE SENTENÇAS (30 TERMOS) ")
    print("=====================================================")

    for termo in TERMOS:
        sincronizar_diariamente(termo)

    print("\n=====================================================")
    print("  SINCRONIZAÇÃO COMPLETA: BANCO ATUALIZADO COM SUCESSO ")
    print("=====================================================")


if __name__ == "__main__":
    main()