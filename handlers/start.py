"""
Start and help command handlers - Yukla Pro (Uzbek)
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - Uzbek"""
    welcome = (
        "⚡ **Yukla Pro**\n\n"
        "Universal Yuklab Oluvchi\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "📸 Instagram · Postlar · Reels\n"
        "🎵 TikTok · Videolar · Rasmlar\n"
        "▶️ YouTube · Videolar · Shorts · Audio\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Yuklab olish uchun havola yuboring\n"
        "Audio uchun qo'shiq nomini yozing\n\n"
        "/help · /info"
    )
    
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - Uzbek"""
    help_text = (
        "📖 **Yukla Pro Qo'llanma**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**Instagram**\n"
        "Postlar · Reels · Karusellar\n\n"
        "**TikTok**\n"
        "Videolar · Rasmlar\n\n"
        "**YouTube**\n"
        "Videolar · Shorts · Audio (MP3)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**Qanday ishlatish**\n"
        "1. Havolani nusxalang\n"
        "2. Shu yerga yuboring\n"
        "3. Yuklab olishni kuting\n\n"
        "💡 Audio uchun qo'shiq nomini yozing\n\n"
        "/start · /info"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command - Uzbek"""
    info_text = (
        "ℹ️ **Yukla Pro**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Versiya · 2.0\n"
        "Holat · Faol\n\n"
        "**Qo'llab-quvvatlaydi**\n"
        "Instagram · TikTok · YouTube\n\n"
        "**Xususiyatlar**\n"
        "Sifat tanlash · Tez yuklash\n"
        "MP3 olish · Qulay interfeys\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "❤️ bilan yaratilgan"
    )
    
    await update.message.reply_text(info_text, parse_mode='Markdown')