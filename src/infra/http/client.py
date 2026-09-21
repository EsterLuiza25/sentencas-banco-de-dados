import requests


URL_API = "https://gateway.cloud.pje.jus.br/banco-sentencas/api/sentencas/buscar"


def buscar_sentencas(termo, tamanho_lote=30, cursor=None):
    payload = {
        "pageOffset": 1,
        "pageSize": tamanho_lote,
        "searchAfterValue": cursor,
        "order": "desc",
        "searchFilters": [{"texto": termo}],
    }

    headers = {
        "content-type": "application/json",
    }

    resposta = requests.post(URL_API, json=payload, headers=headers, timeout=30)

    if resposta.status_code != 200:
        raise Exception(f"Erro HTTP {resposta.status_code}: {resposta.text[:200]!r}")

    return resposta.json()