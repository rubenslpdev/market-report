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
    
    nomes_categorias = {
        "stocks": "💹 <b>AÇÕES</b>",
        "criptos": "🪙 <b>CRIPTOS</b>",
        "moedas": "💵 <b>CÂMBIO</b>",
        "futuros": "📈 <b>FUTUROS</b>"
    }

    linhas = ["📊 <b>Relatório Diário de Mercado</b>"]
    
    for categoria in ["stocks", "criptos", "moedas", "futuros"]:
        if categoria in config["ativos"] and config["ativos"][categoria]:

            linhas.append("\n" + nomes_categorias[categoria])
            linhas.append("━━━━━━━━━━━━━━━")
            linhas.append("")
            
            for item in config["ativos"][categoria]:
                d = buscar_dados_ativo(item["ticker"])
                if d:

                    simbolo = d['ticker'].replace('.SA', '').replace('=X', '')
                    if simbolo == "^BVSP": simbolo = "IBOV"
                    elif simbolo == "BZ=F": simbolo = "BRENT"
                    
                    linhas.append(f"{d['tendencia']} <b>{simbolo}</b>: R$ {d['preco']:,.2f}")
                    
    return "\n".join(linhas)

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

