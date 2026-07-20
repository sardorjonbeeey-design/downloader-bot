"""
Start and help command handlers - Yukla Pro
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome = (
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n"
        "  ⚡ Yukla Pro\n"
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n\n"
        "  Universal Downloader\n\n"
        "  📸 Instagram  ·  Posts  ·  Reels\n"
        "  🎵 TikTok  ·  Videos  ·  Photos\n"
        "  ▶️ YouTube  ·  Videos  ·  Shorts\n"
        "  🎧 Audio  ·  MP3 from YouTube\n\n"
        "  ───────────\n\n"
        "  Paste a link to download.\n"
        "  Type a song name for audio.\n\n"
        "  ❓ /help  ·  ℹ️ /info"
    )
    
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n"
        "  📖 Yukla Pro Guide\n"
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n\n"
        "  📸 Instagram\n"
        "  Posts · Reels · Carousels\n\n"
        "  🎵 TikTok\n"
        "  Videos · Photo Slides\n\n"
        "  ▶️ YouTube\n"
        "  Videos · Shorts · MP3\n\n"
        "  ───────────\n\n"
        "  How to use:\n"
        "  1. Copy a link\n"
        "  2. Paste it here\n"
        "  3. Wait for download\n\n"
        "  💡 Tip: For audio, type song name.\n\n"
        "  🏠 /start  ·  ℹ️ /info"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command"""
    info_text = (
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n"
        "  ℹ️ Yukla Pro\n"
        "▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️▫️\n\n"
        "  Version · 2.0\n"
        "  Status · Online\n\n"
        "  Supported:\n"
        "  · Instagram\n"
        "  · TikTok\n"
        "  · YouTube\n\n"
        "  Features:\n"
        "  · Quality selection\n"
        "  · Fast downloads\n"
        "  · MP3 extraction\n\n"
        "  📱 Made with ❤️"
    )
    
    await update.message.reply_text(info_text, parse_mode='Markdown')