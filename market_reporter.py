import os
import sys
import json
import requests
import yfinance as yf
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def ler_configuracoes(filepath=None):
    if filepath is None:
        filepath = os.path.join(BASE_DIR, "config.json")
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

def buscar_dados_ativo(ticker_symbol):
    try:
        ativo = yf.Ticker(ticker_symbol)
        hist = ativo.history(period="5d")
        if hist.empty or len(hist) < 2: return None
        preco = hist['Close'].iloc[-1]
        variacao = ((preco / hist['Close'].iloc[-2]) - 1) * 100
        return {"ticker": ticker_symbol, "preco": preco, "variacao": variacao}
    except Exception: return None

def formatar_preco(preco):
    fmt = f"{preco:,.0f}" if preco >= 1000 else f"{preco:,.2f}"
    return fmt.replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_relatorio():
    config = ler_configuracoes()
    linhas = ["📊 <b>Resumo do mercado:</b>", ""]
    
    for categoria in ["stocks", "criptos", "moedas", "futuros"]:
        bloco = []
        for item in config["ativos"].get(categoria, []):
            d = buscar_dados_ativo(item["ticker"])
            if not d: continue
            simbolo = d['ticker'].replace('.SA', '').replace('=X', '')
            if simbolo == "^BVSP": simbolo = "IBOV"
            elif simbolo == "BZ=F": simbolo = "BRENT"
            bloco.append(f"{simbolo}: {formatar_preco(d['preco'])} {d['variacao']:+.1f}%")
        if bloco:
            linhas.extend(bloco)
            linhas.append("")

    return "\n".join(linhas).rstrip()

def enviar_telegram(mensagem, chat_id=None):
    alvo_chat_id = chat_id or TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": alvo_chat_id, "text": mensagem, "parse_mode": "HTML"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    # O chat_id pode vir via argumento (pelo listener) ou do .env (pelo cron)
    custom_chat_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Quando executado, ele gera o relatório e envia
    relatorio = gerar_relatorio()
    enviar_telegram(relatorio, custom_chat_id)

