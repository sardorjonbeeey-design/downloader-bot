"""
Start and help command handlers
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = (
        "🎯 *Universal Downloader Bot*\n\n"
        "Send me any link from the following platforms and I'll download it for you:\n\n"
        "📸 *Instagram* - Photos, Reels, Carousels, Stories\n"
        "🎵 *TikTok* - Videos, Slides, Audio\n"
        "▶️ *YouTube* - Videos, Shorts, Audio\n"
        "🎶 *Music* - Search by song name or artist\n\n"
        "Just paste a link or type a song name and I'll handle the rest!\n"
        "No commands needed.\n\n"
        "ℹ️ Use /help for more information"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_message = (
        "📖 *How to use the bot*\n\n"
        "*1. Instagram:*\n"
        "Send any Instagram link (post, reel, story, or profile)\n\n"
        "*2. TikTok:*\n"
        "Send any TikTok video or photo slide link\n\n"
        "*3. YouTube:*\n"
        "Send any YouTube video or Shorts link\n"
        "You can choose quality from the available options\n\n"
        "*4. Music Search:*\n"
        "Simply type a song name or artist + song name\n"
        "Example: \"Imagine Dragons Believer\"\n\n"
        "*Quick Tips:*\n"
        "• The bot detects links automatically\n"
        "• Downloads are cleaned up after sending\n"
        "• Maximum file size: 50MB\n"
        "• Supported audio formats: MP3\n\n"
        "*Commands:*\n"
        "/start - Welcome message\n"
        "/help - This help message"
    )
    await update.message.reply_text(help_message, parse_mode='Markdown')