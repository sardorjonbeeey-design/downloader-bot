"""
Music Handler - Music logikasi FAQAT shu yerda
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.music import search_music, download_music
from handlers.admin import stats_manager

logger = logging.getLogger(__name__)

async def handle_music_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Music qidirish"""
    query = update.message.text.strip()
    
    status_msg = await update.message.reply_text(f"🔍 \"{query}\" qidirilmoqda...")
    
    try:
        results = await search_music(query)
        
        if not results:
            await status_msg.edit_text(
                f"❌ Natija topilmadi\n\n"
                f"\"{query}\"\n\n"
                "Urinib ko'ring:\n"
                "• Boshqa imlo\n"
                "• Artist + qo'shiq nomi"
            )
            return
        
        result = results[0]
        await status_msg.delete()
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎵 MP3 Yuklab olish", callback_data=f"music_download_{result['id']}"),
                InlineKeyboardButton("▶️ Ko'rish", url=result['url'])
            ]
        ])
        
        await update.message.reply_photo(
            photo=result['thumbnail'],
            caption=(
                f"🎵 *{result['title']}*\n"
                f"👤 Artist · {result['artist']}\n"
                f"⏱️ Davomiyligi · {result['duration']}\n\n"
                f"📥 Tanlang:"
            ),
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        context.user_data['music_result'] = result
        stats_manager.add_download(update.effective_user.id, 'music')
        
    except Exception as e:
        logger.error(f"Music xatolik: {str(e)}", exc_info=True)
        await status_msg.edit_text(f"❌ Xatolik: {str(e)[:100]}")

async def handle_music_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Music yuklab olish tugmasi"""
    query = update.callback_query
    await query.answer()
    
    _, action, music_id = query.data.split('_')
    
    if action == 'download':
        result = context.user_data.get('music_result')
        
        if not result or result.get('id') != music_id:
            await query.edit_message_text("❌ Vaqt tugadi. Qayta qidiring.")
            return
        
        await query.edit_message_text("🎵 MP3 yuklanmoqda...")
        
        try:
            file_data, filename, error = await download_music(result['url'])
            
            if file_data:
                await query.message.reply_audio(
                    audio=file_data,
                    title=result['title'],
                    performer=result['artist'],
                    duration=result.get('duration_seconds', 0),
                    filename=filename
                )
                await query.message.delete()
            else:
                # FIXED: No backslash in f-string
                error_msg = error or "Yuklab bo'lmadi"
                await query.edit_message_text(f"❌ {error_msg}")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Xatolik: {str(e)[:60]}")