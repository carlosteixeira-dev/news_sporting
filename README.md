# 🦁 Sporting News Bot

Bot que recolhe notícias diárias do **Sporting CP** dos principais jornais desportivos portugueses e envia um resumo para o **Telegram** todas as manhãs.

---

## 📁 Estrutura do projeto

```
sporting_news/
├── main.py                          # Ponto de entrada
├── scraper.py                       # Recolhe notícias via RSS
├── telegram_bot.py                  # Formata e envia para o Telegram
├── requirements.txt                 # Dependências
└── .github/
    └── workflows/
        └── sporting_news.yml        # Automação com GitHub Actions
```

---

## ⚙️ Como configurar

### 1. Clonar o repositório

```bash
git clone https://github.com/teu-utilizador/sporting-news-bot.git
cd sporting-news-bot
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

Cria um ficheiro `.env` para testes locais (não commites este ficheiro!):

```
TELEGRAM_TOKEN=123456789:ABCdef...
TELEGRAM_CHAT_ID=987654321
```

> Para obter o teu `CHAT_ID`, envia uma mensagem ao bot e acede a:
> `https://api.telegram.org/bot<TOKEN>/getUpdates`

### 4. Testar localmente

```bash
python main.py
```

---

## 🤖 Configurar GitHub Actions

1. Vai ao teu repositório no GitHub
2. Clica em **Settings → Secrets and variables → Actions**
3. Adiciona dois secrets:
   - `TELEGRAM_TOKEN` → o token do teu bot (do BotFather)
   - `TELEGRAM_CHAT_ID` → o teu chat ID

O bot vai correr automaticamente **todos os dias às 8h (hora de Lisboa)**.

Para correr manualmente: separador **Actions → 🦁 Sporting News Bot → Run workflow**.

---

## 📰 Fontes de notícias

| Jornal | Feed RSS |
|--------|----------|
| A Bola | `abola.pt/rss` |
| Record | `record.pt/rss` |
| Maisfutebol | `maisfutebol.iol.pt/rss` |
| O Jogo | `ojogo.pt/rss` |
| Sapo Desporto | `desporto.sapo.pt/futebol/sporting/rss` |

---

## 🛠️ Stack

- **Python 3.11**
- **feedparser** — leitura de RSS
- **requests** — API do Telegram
- **GitHub Actions** — automação gratuita
