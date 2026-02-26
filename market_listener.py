import os
import subprocess
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def relatorio_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quando você digita /relatorio, ele chama o worker como um processo separado"""
    await update.message.reply_text("⏳ Processando relatório...")
    
    # Chama o script worker. A memória sobe apenas durante esta execução.
    try:
        # Usamos o caminho absoluto ou relativo para garantir que funcione no systemd
        script_path = os.path.join(os.path.dirname(__file__), "market_reporter.py")
        subprocess.Popen(["python3", script_path])
        
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao iniciar worker: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot ativo. Digite /relatorio para atualizar.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("relatorio", relatorio_manual))

    print("Ouvinte do Bot iniciado...")
    app.run_polling()
