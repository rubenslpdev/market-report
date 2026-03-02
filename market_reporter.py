import os
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
        hist = ativo.history(period="2mo")
        if hist.empty: return None
        preco_atual = hist['Close'].iloc[-1]
        sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        tendencia = "🟢" if preco_atual > sma_20 else "🔴" if preco_atual < sma_20 else "➖"
        return {
            "ticker": ticker_symbol, "preco": preco_atual,
            "min_7d": hist.tail(7)['Low'].min(), 
            "max_7d": hist.tail(7)['High'].max(), 
            "tendencia": tendencia
        }
    except Exception: return None

def gerar_relatorio():
    config = ler_configuracoes()
    linhas = ["📊 <b>Relatório de Ativos</b>\n"]
    for categoria in ["stocks", "criptos"]:
        for item in config["ativos"][categoria]:
            d = buscar_dados_ativo(item["ticker"])
            if d:
                simbolo = d['ticker'].replace('.SA', '')
                linhas.append(f"<b>{simbolo}</b>: {d['tendencia']} R$ {d['preco']:,.2f}")
    return "\n\n".join(linhas)

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    # Quando executado, ele gera o relatório e envia
    relatorio = gerar_relatorio()
    enviar_telegram(relatorio)

