import os
import json
import requests
import yfinance as yf
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def ler_configuracoes(filepath="config.json"):
    """Lê a lista de ativos do arquivo JSON."""
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

def buscar_dados_ativo(ticker_symbol):
    """Busca os dados do ativo no yfinance e faz os cálculos."""
    try:
        ativo = yf.Ticker(ticker_symbol)
        
        # Puxa 2 meses de histórico
        hist = ativo.history(period="2mo")
        
        if hist.empty:
            return None

        # Preço Atual
        preco_atual = hist['Close'].iloc[-1]

        # Mínimo e Máximo dos últimos 7 pregões
        ultimos_7_dias = hist.tail(7)
        min_7d = ultimos_7_dias['Low'].min()
        max_7d = ultimos_7_dias['High'].max()

        # SMA de 20 períodos
        sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]

        # Lógica de Tendência 
        if preco_atual > sma_20:
            tendencia = "📈"
        elif preco_atual < sma_20:
            tendencia = "📉"
        else:
            tendencia = "➖"

        return {
            "ticker": ticker_symbol,
            "preco": preco_atual,
            "min_7d": min_7d,
            "max_7d": max_7d,
            "tendencia": tendencia
        }

    except Exception as e:
        print(f"Erro ao buscar dados de {ticker_symbol}: {e}")
        return None

def enviar_mensagem_telegram(mensagem):
    """Envia a mensagem montada para o bot do Telegram usando requests."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Erro: TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não encontrados no .env")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML" # Usar HTML para evitar erros com caracteres especiais como o "-" do BTC-USD
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Relatório enviado com sucesso via Telegram!")
    else:
        print(f"Falha ao enviar: {response.status_code} - {response.text}")

def gerar_relatorio():
    """Lê o config, busca os dados e formata a mensagem."""
    config = ler_configuracoes()
    stocks = config["ativos"]["stocks"]
    criptos = config["ativos"]["criptos"]

    linhas_relatorio = []
    
    # Cabeçalho Principal
    linhas_relatorio.append("📊 <b>Relatório Semanal de Ativos</b>")
    linhas_relatorio.append("🏢 <b>Ações (B3) e Índice</b>")

    # Processar Ações Brasileiras (B3)
    for item in stocks:
        symbol = item["ticker"]
        dados = buscar_dados_ativo(symbol)
        if dados:
            nome_amigavel = symbol.replace('.SA', '') # Remove o .SA
            
            bloco_acao = (
                f"<b>{nome_amigavel}</b>\n"
                f"R$ {dados['preco']:.2f} {dados['tendencia']}\n"
                f"└ Min: R$ {dados['min_7d']:.2f} / Max: R$ {dados['max_7d']:.2f}"
            )
            linhas_relatorio.append(bloco_acao)

    linhas_relatorio.append("---")
    linhas_relatorio.append("🪙 <b>Criptomoedas</b>")

    # Processar Criptomoedas
    for item in criptos:
        symbol = item["ticker"]
        dados = buscar_dados_ativo(symbol)
        if dados:
            # Formatação especial para USD ($) com vírgula para milhares
            bloco_cripto = (
                f"<b>{symbol}</b>\n"
                f"$ {dados['preco']:,.2f} {dados['tendencia']}\n"
                f"└ Min: $ {dados['min_7d']:,.2f} / Max: $ {dados['max_7d']:,.2f}"
            )
            linhas_relatorio.append(bloco_cripto)

    # O join com "\n\n" garante que haja uma linha em branco entre cada bloco de ativo e título
    mensagem_final = "\n\n".join(linhas_relatorio)
    enviar_mensagem_telegram(mensagem_final)

if __name__ == "__main__":
    gerar_relatorio()
