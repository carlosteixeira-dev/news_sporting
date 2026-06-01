"""
telegram_bot.py
---------------
Responsável por formatar e enviar o resumo diário de notícias
do Sporting para o Telegram.

Bibliotecas usadas:
- requests : para fazer chamadas HTTP à API do Telegram
- os       : para ler variáveis de ambiente (token, chat_id)
"""

import requests  # pip install requests
import os
import re
from datetime import datetime


# ---------------------------------------------------------------------------
# 1. LER CREDENCIAIS DAS VARIÁVEIS DE AMBIENTE
# ---------------------------------------------------------------------------
# Nunca coloques o token diretamente no código!
# Usa variáveis de ambiente (GitHub Secrets no Actions, ou .env localmente).
#
# No GitHub Actions, defines:
#   TELEGRAM_TOKEN  → o token do teu bot (do BotFather)
#   TELEGRAM_CHAT_ID → o teu chat ID pessoal ou grupo

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


# ---------------------------------------------------------------------------
# 2. FUNÇÃO: enviar uma mensagem para o Telegram
# ---------------------------------------------------------------------------
def enviar_resumo_diario(noticias: list[dict]) -> None:
    print("DEBUG — entrei no enviar_resumo_diario")  # adiciona esta linha
    mensagem = formatar_mensagem(noticias)


def enviar_mensagem(texto: str) -> bool:
    """
    Envia uma mensagem de texto para o Telegram via API.

    A API do Telegram recebe um POST com:
        - chat_id : para quem enviar
        - text    : o texto da mensagem
        - parse_mode : "HTML" permite usar <b>, <i>, etc. na mensagem

    Devolve True se o envio foi bem sucedido, False caso contrário.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não definidos!")
        return False

    # URL da API do Telegram para enviar mensagens
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    # Dados a enviar no POST
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",           # permite formatação HTML
        "disable_web_page_preview": True  # não mostra pré-visualização de links
    }

    try:
        resposta = requests.post(url, data=payload, timeout=10)

        if resposta.status_code == 200:
            print("✅ Mensagem enviada com sucesso!")
            return True
        else:
            print(f"❌ Erro ao enviar: {resposta.status_code} - {resposta.text}")
            return False

    except requests.exceptions.RequestException as erro:
        print(f"❌ Erro de ligação: {erro}")
        return False


# ---------------------------------------------------------------------------
# 3. FUNÇÃO: formatar a lista de notícias numa mensagem bonita
# ---------------------------------------------------------------------------

def limpar_texto(texto: str) -> str:
    # converte para string caso não seja
    texto = str(texto)
    # remove <![CDATA[ ... ]]> em todas as variantes
    texto = re.sub(r"<!\[CDATA\[", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\]\]>", "", texto)
    # remove qualquer tag HTML restante
    texto = re.sub(r"<[^>]+>", "", texto)
    return texto.strip()


def formatar_mensagem(noticias: list[dict]) -> str:
    """
    Recebe a lista de notícias (dicionários) e devolve uma string
    formatada em HTML para enviar pelo Telegram.

    Exemplo de output:
        🦁 SPORTING CP — Notícias de hoje (12 Jun)
        ━━━━━━━━━━━━━━━━━━━━━━
        📰 A Bola
        • <a href="...">Sporting vence dérbi</a>
        ...
    """
    # Data de hoje formatada em português
    hoje = datetime.now().strftime("%d %b %Y")

    # Cabeçalho da mensagem
    linhas = [
        f"🦁 <b>SPORTING CP — Notícias de hoje ({hoje})</b>",
        "━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    if not noticias:
        linhas.append("Nenhuma notícia encontrada hoje. 😴")
        return "\n".join(linhas)

    # Agrupamos as notícias por jornal para ficar mais organizado
    # Usamos um dicionário: { "A Bola": [...], "Record": [...], ... }
    por_jornal = {}

    for noticia in noticias:
        jornal = noticia["jornal"]

        # Se o jornal ainda não está no dicionário, criamos a lista
        if jornal not in por_jornal:
            por_jornal[jornal] = []

        por_jornal[jornal].append(noticia)

    # Construímos a mensagem jornal a jornal
    for jornal, artigos in por_jornal.items():
        linhas.append(f"📰 <b>{jornal}</b>")

        for artigo in artigos:
            titulo = limpar_texto(artigo["titulo"])
            link = limpar_texto(artigo["link"])
            print(f"DEBUG titulo: {repr(titulo)}")
            print(f"DEBUG link: {repr(link)}")

            # Cada artigo é um link clicável no Telegram
            # <a href="URL">Título</a> — sintaxe HTML do Telegram
            linhas.append(f"• <a href=\"{link}\">{titulo}</a>")

        linhas.append("")  # linha em branco entre jornais

    # Rodapé
    total = len(noticias)
    linhas.append(f"━━━━━━━━━━━━━━━━━━━━━━")
    linhas.append(f"📊 Total: {total} notícia{'s' if total != 1 else ''}")

    # Juntamos todas as linhas com quebra de linha
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# 4. FUNÇÃO PRINCIPAL: formatar e enviar
# ---------------------------------------------------------------------------

def enviar_resumo_diario(noticias: list[dict]) -> None:
    """
    Recebe a lista de notícias, formata-as e envia para o Telegram.
    Esta é a função que o main.py vai chamar.
    """
    mensagem = formatar_mensagem(noticias)

    print("\n--- MENSAGEM A ENVIAR ---")
    print(mensagem)
    print("-------------------------\n")

    # O Telegram tem limite de 4096 caracteres por mensagem.
    # Se a mensagem for muito longa, dividimos em partes.
    LIMITE = 4096

    if len(mensagem) <= LIMITE:
        # Mensagem cabe numa só — enviamos diretamente
        print(repr(mensagem))
        enviar_mensagem(mensagem)
    else:
        # Dividimos por parágrafos (linhas vazias)
        partes = mensagem.split("\n\n")
        parte_atual = ""

        for parte in partes:
            # Se adicionar esta parte ainda cabe no limite, adicionamos
            if len(parte_atual) + len(parte) + 2 <= LIMITE:
                parte_atual += parte + "\n\n"
            else:
                # Senão, enviamos o que temos e começamos uma nova parte
                if parte_atual:
                    enviar_mensagem(parte_atual.strip())
                parte_atual = parte + "\n\n"

        # Enviamos o resto
        if parte_atual:
            enviar_mensagem(parte_atual.strip())


# ---------------------------------------------------------------------------
# 5. TESTE LOCAL
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Notícias falsas para testar a formatação sem chamar o scraper
    noticias_teste = [
        {
            "jornal": "A Bola",
            "titulo": "Sporting vence Benfica no dérbi de Lisboa",
            "link": "https://www.abola.pt/exemplo",
            "resumo": "Os leões derrotaram o rival com dois golos..."
        },
        {
            "jornal": "Record",
            "titulo": "Leões contratam avançado internacional",
            "link": "https://www.record.pt/exemplo",
            "resumo": "Reforço chega de Alvalade esta semana..."
        },
        {
            "jornal": "A Bola",
            "titulo": "Sporting CP na final da Taça de Portugal",
            "link": "https://www.abola.pt/exemplo2",
            "resumo": ""
        },
    ]

    enviar_resumo_diario(noticias_teste)
