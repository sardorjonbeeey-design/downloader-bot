"""
Pinterest Handler - Pinterest logikasi FAQAT shu yerda
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.pinterest import download_pinterest
from handlers.admin import stats_manager

logger = logging.getLogger(__name__)

async def handle_pinterest(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE, status_msg):
    """Pinterest logikasi"""
    user_id = update.effective_user.id
    
    result = await download_pinterest(url)
    
    if not result:
        await status_msg.edit_text(
            "❌ Pinterest yuklab bo'lmadi\n\n"
            "• Rasm/video yopiq bo'lishi mumkin\n"
            "• Havola noto'g'ri"
        )
        return None
    
    stats_manager.add_download(user_id, 'pinterest')
    return result