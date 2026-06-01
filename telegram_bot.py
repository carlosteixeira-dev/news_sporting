import requests
import os
import re
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def limpar_texto(texto: str) -> str:
    texto = str(texto)
    texto = re.sub(r"<!\[CDATA\[", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\]\]>", "", texto)
    texto = re.sub(r"<[^>]+>", "", texto)
    return texto.strip()


def enviar_mensagem(texto: str) -> bool:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não definidos!")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
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


def formatar_mensagem(noticias: list[dict]) -> str:
    hoje = datetime.now().strftime("%d %b %Y")

    linhas = [
        f"🦁 <b>SPORTING CP — Notícias de hoje ({hoje})</b>",
        "━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]

    if not noticias:
        linhas.append("Nenhuma notícia encontrada hoje. 😴")
        return "\n".join(linhas)

    por_jornal = {}
    for noticia in noticias:
        jornal = noticia["jornal"]
        if jornal not in por_jornal:
            por_jornal[jornal] = []
        por_jornal[jornal].append(noticia)

    for jornal, artigos in por_jornal.items():
        linhas.append(f"📰 <b>{jornal}</b>")
        for artigo in artigos:
            titulo = limpar_texto(artigo["titulo"])
            link = artigo["link"].strip()
            print(f"DEBUG titulo: {repr(titulo)}")
            print(f"DEBUG link: {repr(link)}")
            linhas.append(f"• <a href=\"{link}\">{titulo}</a>")
        linhas.append("")

    total = len(noticias)
    linhas.append("━━━━━━━━━━━━━━━━━━━━━━")
    linhas.append(f"📊 Total: {total} notícia{'s' if total != 1 else ''}")

    return "\n".join(linhas)


def enviar_resumo_diario(noticias: list[dict]) -> None:
    mensagem = formatar_mensagem(noticias)

    print("\n--- MENSAGEM A ENVIAR ---")
    print(mensagem)
    print(f"\nDEBUG REPR: {repr(mensagem)}")
    print("-------------------------\n")

    enviar_mensagem(mensagem)
