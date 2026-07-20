#!/usr/bin/env python3
"""
Yukla Pro - All-in-One Downloader Bot
"""
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config import config
from handlers import (
    start_command,
    help_command,
    info_command,
    handle_url,
    handle_youtube_callback,
    handle_music_callback,
)
from handlers.admin import stats_command, reset_stats, stats_manager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

def main():
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN not found")
        return
    
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("resetstats", reset_stats))
    
    # Handlers
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_url
        )
    )
    
    application.add_handler(CallbackQueryHandler(handle_youtube_callback, pattern=r'^quality_.*'))
    application.add_handler(CallbackQueryHandler(handle_music_callback, pattern=r'^music_.*'))
    
    logger.info(f"📊 Stats: {stats_manager.stats['total_downloads']} total downloads")
    logger.info("⚡ Yukla Pro is starting...")
    application.run_polling(allowed_updates=['message', 'callback_query'])

if __name__ == '__main__':
    main()