import os
import sys
import json
import requests
import numpy as np
import yfinance as yf
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- Limiares ---
# Stocks: RSI padrão (30/70). Criptos: mais tolerante (35/80).
LIMIAR = {
    "stocks": {"rsi_barato": 40, "rsi_caro": 70, "zscore_barato": -1.5, "zscore_caro": 1.5},
    "criptos": {"rsi_barato": 40, "rsi_caro": 80, "zscore_barato": -1.5, "zscore_caro": 1.5},
}


def ler_configuracoes():
    filepath = os.path.join(BASE_DIR, "config.json")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def calcular_rsi(closes, periodo=14):
    deltas = np.diff(closes)
    ganhos = np.where(deltas > 0, deltas, 0)
    perdas = np.where(deltas < 0, -deltas, 0)
    media_ganho = np.mean(ganhos[-periodo:])
    media_perda = np.mean(perdas[-periodo:])
    if media_perda == 0:
        return 100.0
    rs = media_ganho / media_perda
    return 100 - (100 / (1 + rs))


def calcular_adx(hist, periodo=14):
    high = hist["High"].values
    low = hist["Low"].values
    close = hist["Close"].values
    n = len(close)
    if n < periodo + 1:
        return None

    tr_list, dm_pos, dm_neg = [], [], []
    for i in range(1, n):
        tr = max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))
        tr_list.append(tr)
        dm_pos.append(max(high[i] - high[i - 1], 0) if (high[i] - high[i - 1]) > (low[i - 1] - low[i]) else 0)
        dm_neg.append(max(low[i - 1] - low[i], 0) if (low[i - 1] - low[i]) > (high[i] - high[i - 1]) else 0)

    atr = np.mean(tr_list[-periodo:])
    if atr == 0:
        return None
    pdi = (np.mean(dm_pos[-periodo:]) / atr) * 100
    mdi = (np.mean(dm_neg[-periodo:]) / atr) * 100
    dx = abs(pdi - mdi) / (pdi + mdi) * 100 if (pdi + mdi) > 0 else 0
    return dx


def analisar_ativo(ticker, categoria):
    limiar = LIMIAR[categoria]
    try:
        hist = yf.Ticker(ticker).history(period="1y")
        hist = hist.dropna(subset=["Close"])
        if len(hist) < 50:
            return None

        closes = hist["Close"].values
        ultimo_preco = closes[-1]

        # RSI
        rsi = calcular_rsi(closes) if len(closes) > 14 else None

        # Z-Score (janela 20 dias)
        media = np.mean(closes[-20:])
        desvio = np.std(closes[-20:])
        zscore = (ultimo_preco - media) / desvio if desvio > 0 else 0

        # SMAs
        sma_50 = np.mean(closes[-50:]) if len(closes) >= 50 else None
        sma_200 = np.mean(closes[-200:]) if len(closes) >= 200 else None

        # ADX
        adx = calcular_adx(hist)

        # --- Status de Preço ---
        if rsi is not None and rsi < limiar["rsi_barato"] and zscore < limiar["zscore_barato"]:
            status_preco = "🟢 Barato"
        elif rsi is not None and rsi > limiar["rsi_caro"] and zscore > limiar["zscore_caro"]:
            status_preco = "🔴 Caro"
        elif rsi is not None and rsi < limiar["rsi_barato"]:
            status_preco = "🟡 Pos. Barato"
        elif rsi is not None and rsi > limiar["rsi_caro"]:
            status_preco = "🟡 Pos. Caro"
        else:
            status_preco = "⚪ Neutro"

        # --- Status de Tendência ---
        acima_sma200 = sma_200 is not None and ultimo_preco > sma_200
        adx_forte = adx is not None and adx > 25
        if acima_sma200 and adx_forte:
            status_tendencia = "📈 Forte"
        elif acima_sma200:
            status_tendencia = "↗️ Moderada"
        elif adx_forte:
            status_tendencia = "⚡ Volátil"
        else:
            status_tendencia = "📉 Fraca"

        # --- Decisão de DCA ---
        if "Barato" in status_preco and "Forte" in status_tendencia:
            decisao = "💰 AUMENTAR APORTE (2x) — Oportunidade de Ouro"
        elif "Neutro" in status_preco and "Forte" in status_tendencia:
            decisao = "✅ MANTER APORTE — Continuidade"
        elif "Caro" in status_preco:
            decisao = "⚠️ REDUZIR APORTE (0.5x) — Ativo Caro"
        elif "Fraca" in status_tendencia or "Volátil" in status_tendencia:
            decisao = "🛑 SUSPENDER / ACUMULAR CAIXA — Tendência Fraca"
        else:
            decisao = "✅ MANTER APORTE — Continuidade"

        simbolo = ticker.replace(".SA", "").replace("-USD", "").replace("=X", "")
        rsi_str = f"{rsi:.1f}" if rsi is not None else "N/D"
        adx_str = f"{adx:.1f}" if adx is not None else "N/D"

        return {
            "simbolo": simbolo,
            "preco": ultimo_preco,
            "rsi": rsi_str,
            "zscore": f"{zscore:.2f}",
            "adx": adx_str,
            "status_preco": status_preco,
            "status_tendencia": status_tendencia,
            "decisao": decisao,
        }
    except Exception:
        return None


def gerar_alerta_dca():
    config = ler_configuracoes()
    linhas = ["📊 <b>Alerta DCA Inteligente</b>", ""]

    for categoria in ["stocks", "criptos"]:
        ativos = config["ativos"].get(categoria, [])
        if not ativos:
            continue

        label = "📈 Stocks" if categoria == "stocks" else "₿ Criptos"
        linhas.append(f"<b>{label}</b>")

        for item in ativos:
            dados = analisar_ativo(item["ticker"], categoria)
            if not dados:
                continue
            linhas.append(
                f"\n<b>{dados['simbolo']}</b>\n"
                f"  Preço: {dados['status_preco']}  |  Tend.: {dados['status_tendencia']}\n"
                f"  RSI: {dados['rsi']}  |  Z-Score: {dados['zscore']}  |  ADX: {dados['adx']}\n"
                f"  ➡️ {dados['decisao']}"
            )

        linhas.append("")

    return "\n".join(linhas).rstrip()


def enviar_telegram(mensagem, chat_id=None):
    alvo = chat_id or TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": alvo, "text": mensagem, "parse_mode": "HTML"})


if __name__ == "__main__":
    custom_chat_id = sys.argv[1] if len(sys.argv) > 1 else None
    alerta = gerar_alerta_dca()
    enviar_telegram(alerta, custom_chat_id)
