from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os

# .env faylni yuklash
load_dotenv()

# Bot tokenini olish
BOT_TOKEN = os.getenv("BOT_TOKEN")


# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Assalomu alaykum!\n\n"
        "Menga TikTok, YouTube yoki Instagram havolasini yuboring.\n"
        "Men siz uchun videoni yuklab beraman! 🚀"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # /start komandasi
    app.add_handler(CommandHandler("start", start))

    print("✅ Bot ishga tushdi...")

    app.run_polling()


if __name__ == "__main__":
    main()