#!/usr/bin/env python3
"""
Telegram Universal Downloader Bot
Main entry point for the application
"""
import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config import config
from handlers.start import start_command, help_command
from handlers.download import handle_url, handle_callback
from handlers.music import handle_music_search, handle_music_callback

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the bot"""
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables")
        return
    
    # Create application
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Handle URLs and music searches
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_url
        )
    )
    
    # Handle callback queries
    application.add_handler(CallbackQueryHandler(handle_callback, pattern=r'^(quality|music)_.*'))
    application.add_handler(CallbackQueryHandler(handle_music_callback, pattern=r'^music_.*'))
    
    # Start bot
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=['message', 'callback_query'])

if __name__ == '__main__':
    main()