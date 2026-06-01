"""
capas.py
--------
Faz scraping das capas dos jornais desportivos portugueses
a partir do site vercapas.com e envia-as para o Telegram.

Bibliotecas usadas:
- requests      : para fazer pedidos HTTP
- beautifulsoup4: para extrair a imagem da página HTML
- os            : para ler variáveis de ambiente
"""

import requests
from bs4 import BeautifulSoup
import os

# credenciais do Telegram (as mesmas do telegram_bot.py)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# lista de jornais com o URL da página de capa no vercapas.com
JORNAIS = [
    {
        "nome": "A Bola",
        "url": "https://www.vercapas.com/capa/a-bola.html"
    },
    {
        "nome": "Record",
        "url": "https://www.vercapas.com/capa/record.html"
    },
    {
        "nome": "O Jogo",
        "url": "https://www.vercapas.com/capa/o-jogo.html"
    },
]


def obter_url_capa(url_pagina: str) -> str | None:
    """
    Faz scraping da página do vercapas.com e extrai o URL da imagem da capa.
    Devolve o URL da imagem ou None se não encontrar.
    """
    try:
        # simula um browser para evitar bloqueios
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        # faz o pedido HTTP à página
        resposta = requests.get(url_pagina, headers=headers, timeout=10)

        # verifica se o pedido foi bem sucedido
        if resposta.status_code != 200:
            print(f"⚠️  Erro HTTP {resposta.status_code} ao aceder a {url_pagina}")
            return None

        # usa o BeautifulSoup para interpretar o HTML
        soup = BeautifulSoup(resposta.content, "html.parser")

        # procura a meta tag og:image que tem o URL da imagem da capa
        meta_imagem = soup.find("meta", property="og:image")

        if meta_imagem and meta_imagem.get("content"):
            return meta_imagem["content"]

        # alternativa: procura a imagem diretamente no HTML
        imagem = soup.find("img", src=lambda s: s and "covers" in s)
        if imagem:
            src = imagem.get("src", "")
            # garante que o URL é absoluto
            if src.startswith("http"):
                return src
            return "https://imgs.vercapas.com" + src

        return None

    except Exception as erro:
        print(f"⚠️  Erro ao obter capa: {erro}")
        return None


def enviar_foto_telegram(url_imagem: str, legenda: str) -> bool:
    """
    Envia uma imagem para o Telegram usando o URL da imagem.
    A legenda aparece por baixo da imagem.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não definidos!")
        return False

    # endpoint da API do Telegram para enviar fotos
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": url_imagem,       # URL da imagem
        "caption": legenda,        # texto por baixo da imagem
        "parse_mode": "HTML"       # permite formatação HTML na legenda
    }

    try:
        resposta = requests.post(url, data=payload, timeout=10)

        if resposta.status_code == 200:
            print(f"✅ Capa enviada: {legenda}")
            return True
        else:
            print(f"❌ Erro ao enviar capa: {resposta.status_code} - {resposta.text}")
            return False

    except requests.exceptions.RequestException as erro:
        print(f"❌ Erro de ligação: {erro}")
        return False


def enviar_capas() -> None:
    """
    Percorre todos os jornais, obtém a URL da capa e envia para o Telegram.
    Esta é a função que o main.py vai chamar.
    """
    print("\n📰 A recolher capas dos jornais...\n")

    for jornal in JORNAIS:
        nome = jornal["nome"]
        url_pagina = jornal["url"]

        print(f"🔍 A obter capa: {nome}...")

        # obtém o URL da imagem da capa
        url_imagem = obter_url_capa(url_pagina)

        if url_imagem:
            # envia a imagem para o Telegram com o nome do jornal como legenda
            legenda = f"📰 <b>Capa de hoje — {nome}</b>"
            enviar_foto_telegram(url_imagem, legenda)
        else:
            print(f"⚠️  Não foi possível obter a capa de {nome}")


# teste local
if __name__ == "__main__":
    enviar_capas()
