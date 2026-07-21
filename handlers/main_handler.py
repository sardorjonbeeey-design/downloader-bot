"""
Main Handler - Yukla Pro
ONE FILE with CLEAR sections for each platform
"""
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.instagram import download_instagram
from services.tiktok import download_tiktok
from services.youtube import download_youtube, download_youtube_audio
from services.pinterest import download_pinterest
from services.music import search_music, download_music
from handlers.admin import stats_manager
from handlers.youtube import handle_youtube, youtube_callback_handler
from handlers.music import handle_music_search, handle_music_callback

logger = logging.getLogger(__name__)

# ... rest of the file