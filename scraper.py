"""
scraper.py
----------
Recolhe notícias sobre o Sporting CP a partir dos feeds RSS
dos principais jornais desportivos portugueses.

Bibliotecas usadas:
- feedparser : lê feeds RSS de forma simples
- datetime   : para filtrar apenas notícias de hoje
"""

import feedparser  # pip install feedparser
from datetime import datetime, timezone
import re


# ---------------------------------------------------------------------------
# 1. FEEDS RSS DOS JORNAIS
# ---------------------------------------------------------------------------
# Cada entrada é um dicionário com o nome do jornal e o URL do feed RSS.
# O feedparser vai descarregar e interpretar cada feed automaticamente.

FEEDS = [
    {
        "jornal": "Record",
        "url": "https://www.record.pt/rss"
    },
    {
        "jornal": "Maisfutebol",
        "url": "https://maisfutebol.iol.pt/rss"
    },
    {
        "jornal": "A Bola",
        "url": "https://www.abola.pt/rss/index.aspx"  # URL original sem redirect
    },
    {
        "jornal": "Sapo Desporto",
        "url": "https://desporto.sapo.pt/futebol/sporting-cp/rss.xml"
    },
    {
    "jornal": "Visão de Mercado",
    "url": "https://blogvisaodemercado.pt/feeds/posts/default?alt=rss"
    },
]


# ---------------------------------------------------------------------------
# 2. PALAVRAS-CHAVE PARA FILTRAR NOTÍCIAS DO SPORTING
# ---------------------------------------------------------------------------
# Se o título ou resumo de uma notícia contiver qualquer uma destas palavras,
# consideramos que é sobre o Sporting CP.

PALAVRAS_CHAVE = [
    "sporting",
    "sporting cp",
    "leões",
    "alvalade",
    "rui borges",   # atualiza com o nome do treinador atual se necessário
    "sporting clube de portugal",
]


# ---------------------------------------------------------------------------
# 3. FUNÇÃO: verificar se a notícia é sobre o Sporting
# ---------------------------------------------------------------------------

def e_noticia_do_sporting(titulo: str, resumo: str = "") -> bool:
    """
    Recebe o título e o resumo (opcional) de uma notícia.
    Devolve True se contiver alguma palavra-chave do Sporting.

    Exemplo:
        e_noticia_do_sporting("Sporting vence dérbi") → True
        e_noticia_do_sporting("Benfica contrata avançado") → False
    """
    # Juntamos título + resumo e convertemos para minúsculas
    # para a comparação não ser sensível a maiúsculas/minúsculas
    texto = (titulo + " " + resumo).lower()

    # Percorremos todas as palavras-chave
    for palavra in PALAVRAS_CHAVE:
        if palavra.lower() in texto:
            return True  # Basta uma palavra-chave para ser considerada

    return False  # Nenhuma palavra-chave encontrada


# ---------------------------------------------------------------------------
# 4. FUNÇÃO: verificar se a notícia é de hoje
# ---------------------------------------------------------------------------

def e_de_hoje(entry) -> bool:
    # se não tiver data, incluímos sempre
    if not hasattr(entry, "published_parsed") or entry.published_parsed is None:
        return True

    # converte para datetime UTC
    data_noticia = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

    # hora atual UTC
    agora = datetime.now(timezone.utc)

    # inclui notícias das últimas 24 horas em vez de só "hoje"
    diferenca = agora - data_noticia
    return diferenca.total_seconds() <= 86400  # 86400 segundos = 24 horas

# ---------------------------------------------------------------------------
# 5. FUNÇÃO PRINCIPAL: recolher todas as notícias do Sporting de hoje
# ---------------------------------------------------------------------------

def recolher_noticias() -> list[dict]:
    """
    Percorre todos os feeds RSS definidos em FEEDS.
    Para cada feed, filtra as notícias de hoje que sejam sobre o Sporting.
    Devolve uma lista de dicionários com as notícias encontradas.

    Cada notícia tem:
        - jornal  : nome do jornal
        - titulo  : título da notícia
        - link    : URL para a notícia completa
        - resumo  : primeiro parágrafo (se disponível)
    """
    noticias = []

    for feed_info in FEEDS:
        jornal = feed_info["jornal"]
        url = feed_info["url"]

        print(f"🔍 A recolher feed: {jornal}...")

        try:
            # feedparser.parse() descarrega e interpreta o RSS automaticamente
            feed = feedparser.parse(url)

            # feed.entries é a lista de artigos do feed
            for entry in feed.entries:
                titulo = re.sub(r"<!\[CDATA\[|\]\]>", "", entry.get("title", ""), flags=re.IGNORECASE).strip()
                link = re.sub(r"<!\[CDATA\[|\]\]>", "", entry.get("link", ""), flags=re.IGNORECASE).strip()
                link = re.sub(r"<[^>]+>", "", link).strip()

                # remove CDATA e tags HTML do link caso venha contaminado pelo RSS
                link = re.sub(r"<!\[CDATA\[|\]\]>", "", entry.get("link", ""), flags=re.IGNORECASE).strip()
                link = re.sub(r"<[^>]+>", "", link).strip()

                # Alguns feeds têm resumo, outros não
                resumo = entry.get("summary", "")

                # Remove tags HTML do resumo (ex: <p>, <b>, etc.)
                resumo_limpo = re.sub(r"<[^>]+>", "", resumo).strip()

                # Filtramos: só notícias de hoje E sobre o Sporting
                if e_de_hoje(entry) and e_noticia_do_sporting(titulo, resumo_limpo):
                    noticias.append({
                        "jornal": jornal,
                        "titulo": titulo,
                        "link": link,
                        "resumo": resumo_limpo[:200],  # máximo 200 caracteres
                    })

        except Exception as erro:
            # Se um feed falhar (ex: site em baixo), continuamos com os outros
            print(f"⚠️  Erro ao recolher {jornal}: {erro}")

    print(f"\n✅ Total de notícias do Sporting encontradas: {len(noticias)}")
    return noticias


# ---------------------------------------------------------------------------
# 6. TESTE LOCAL
# ---------------------------------------------------------------------------
# Este bloco só corre quando executas o ficheiro diretamente:
#   python scraper.py
# Não corre quando o ficheiro é importado por outro módulo (ex: main.py).

if __name__ == "__main__":
    noticias = recolher_noticias()

    if not noticias:
        print("Nenhuma notícia encontrada hoje.")
    else:
        for n in noticias:
            print(f"\n[{n['jornal']}] {n['titulo']}")
            print(f"🔗 {n['link']}")
