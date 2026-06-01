"""
main.py
-------
Ponto de entrada do projeto.
Orquestra o scraper e o bot do Telegram:
  1. Recolhe notícias do Sporting via RSS
  2. Envia o resumo para o Telegram

Para correr localmente:
    python main.py

No GitHub Actions, este ficheiro é chamado automaticamente às 8h.
"""

from scraper import recolher_noticias
from telegram_bot import enviar_resumo_diario


def main():
    print("🦁 Sporting News Bot — a iniciar...\n")

    # Passo 1: recolher notícias dos feeds RSS
    noticias = recolher_noticias()

    # Passo 2: enviar resumo para o Telegram
    # (mesmo que não haja notícias, enviamos mensagem a informar)
    enviar_resumo_diario(noticias)

    print("\n🏁 Concluído!")


# Só executa se corrermos este ficheiro diretamente
if __name__ == "__main__":
    main()
