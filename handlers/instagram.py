"""
Instagram Handler - Instagram logikasi FAQAT shu yerda
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.instagram import download_instagram
from handlers.admin import stats_manager

logger = logging.getLogger(__name__)

async def handle_instagram(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE, status_msg):
    """Instagram logikasi"""
    user_id = update.effective_user.id
    
    result = await download_instagram(url)
    
    if not result:
        await status_msg.edit_text(
            "❌ Instagram yuklab bo'lmadi\n\n"
            "• Post yopiq (private) bo'lishi mumkin\n"
            "• Havola noto'g'ri\n"
            "• Qayta urinib ko'ring"
        )
        return None
    
    stats_manager.add_download(user_id, 'instagram')
    return result