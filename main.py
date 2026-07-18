#!/usr/bin/env python3
"""
Telegram Universal Downloader Bot
Main entry point for the application
"""
import logging
import os
import sys
import threading
import fcntl
from flask import Flask
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

# Create health check server
health_app = Flask(__name__)

@health_app.route('/')
def health():
    return "Bot is running!", 200

def start_health_server():
    """Start HTTP server for Render health checks"""
    port = int(os.environ.get('PORT', 10000))
    health_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def check_single_instance():
    """Prevent multiple bot instances"""
    try:
        lock_file = open('/tmp/bot.lock', 'w')
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_file
    except:
        logger.error("Another instance is already running! Exiting...")
        sys.exit(1)

def main():
    """Main function to run the bot"""
    # Check for single instance
    lock = check_single_instance()
    
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables")
        return
    
    # Start health check server in background
    logger.info("Starting health check server on port 10000...")
    threading.Thread(target=start_health_server, daemon=True).start()
    
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
    
    try:
        application.run_polling(allowed_updates=['message', 'callback_query'])
    finally:
        if lock:
            lock.close()

if __name__ == '__main__':
    main()