import html
import re


def transformar_em_html(texto):
    if not texto:
        return ""

    paragrafos = []

    for bloco in re.split(r"\n\s*\n", texto):
        bloco = bloco.strip()
        if bloco:
            bloco = html.escape(bloco).replace("\n", "<br>")
            paragrafos.append(f"<p>{bloco}</p>")

    return "\n".join(paragrafos)


def achar_datas(texto):
    if not texto:
        return ""

    padroes = [
        r"\b\d{2}/\d{2}/\d{4}\b",
        r"\b\d{2}-\d{2}-\d{4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}\s+de\s+[a-zç]+\s+de\s+\d{4}\b",
    ]

    datas = []

    for padrao in padroes:
        datas += re.findall(padrao, texto, flags=re.IGNORECASE)

    return ", ".join(sorted(set(datas)))
