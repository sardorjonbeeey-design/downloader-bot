"""
TikTok Handler - TikTok logikasi FAQAT shu yerda
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.tiktok import download_tiktok
from handlers.admin import stats_manager

logger = logging.getLogger(__name__)

async def handle_tiktok(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE, status_msg):
    """TikTok logikasi"""
    user_id = update.effective_user.id
    
    result = await download_tiktok(url)
    
    if not result:
        await status_msg.edit_text(
            "❌ TikTok yuklab bo'lmadi\n\n"
            "• Video yopiq (private) bo'lishi mumkin\n"
            "• Havola noto'g'ri\n"
            "• Qayta urinib ko'ring"
        )
        return None
    
    stats_manager.add_download(user_id, 'tiktok')
    return result