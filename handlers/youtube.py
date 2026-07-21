"""
YouTube Handler - All YouTube logic in ONE place
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.youtube import download_youtube, download_youtube_audio
from handlers.admin import stats_manager

logger = logging.getLogger(__name__)

async def handle_youtube(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE, status_msg):
    """All YouTube logic here"""
    user_id = update.effective_user.id
    
    result = await download_youtube(url)
    
    if not result:
        await status_msg.edit_text(
            "❌ YouTube yuklab bo'lmadi\n\n"
            "• Video yopiq (private)\n"
            "• Havola noto'g'ri\n"
            "• YouTube cookies kerak"
        )
        return None
    
    # Show quality selection
    if 'qualities' in result:
        await status_msg.delete()
        keyboard = build_youtube_keyboard(result, result.get('video_id', 'unknown'))
        caption = build_youtube_caption(result)
        
        if result.get('thumbnail'):
            await update.message.reply_photo(
                photo=result['thumbnail'],
                caption=caption,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                caption,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        
        context.user_data['youtube_video'] = result
        stats_manager.add_download(user_id, 'youtube')
        return None
    
    return result

def build_youtube_keyboard(result: dict, video_id: str) -> InlineKeyboardMarkup:
    """Build YouTube quality keyboard"""
    qualities = result.get('qualities', {})
    keyboard = []
    
    quality_order = ['144p', '240p', '360p', '480p', '720p', '1080p']
    row = []
    
    for quality in quality_order:
        if quality in qualities:
            size = qualities[quality].get('size', '')
            label = f"{quality}" if not size else f"{quality} {size}"
            row.append(InlineKeyboardButton(label, callback_data=f"youtube_{quality}_{video_id}"))
            if len(row) == 3:
                keyboard.append(row)
                row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([
        InlineKeyboardButton("🎵 MP3 Audio", callback_data=f"youtube_audio_{video_id}"),
        InlineKeyboardButton("🖼️ Ko'rish", callback_data=f"youtube_preview_{video_id}")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def build_youtube_caption(result: dict) -> str:
    """Build YouTube caption - FIXED: no backslash in f-string"""
    title = result.get('title', "Noma'lum")
    duration = result.get('duration', "Noma'lum")
    
    return (
        f"▶️ *YouTube*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎬 *{title}*\n"
        f"⏱️ Davomiyligi: {duration}\n\n"
        f"📥 *Sifatni tanlang:*\n"
        f"• Video: MP4\n"
        f"• Audio: MP3 (192kbps)"
    )

async def youtube_callback_handler(query, context):
    """Handle YouTube callbacks"""
    data = query.data
    parts = data.split('_')
    
    if len(parts) < 3:
        await query.edit_message_text("❌ Noto'g'ri tanlov")
        return
    
    action = parts[1]
    video_id = parts[2]
    
    video_info = context.user_data.get('youtube_video', {})
    if not video_info or video_info.get('video_id') != video_id:
        await query.edit_message_text("❌ Vaqt tugadi. Havolani qayta yuboring.")
        return
    
    if action == 'preview':
        await show_preview(query, video_info)
        return
    
    if action == 'audio':
        await download_audio(query, context, video_info)
        return
    
    await download_video_quality(query, context, video_info, action)

async def show_preview(query, video_info):
    """Show video preview"""
    thumbnail = video_info.get('thumbnail')
    title = video_info.get('title', 'Video')
    duration = video_info.get('duration', "Noma'lum")
    
    if thumbnail:
        await query.edit_message_caption(
            caption=f"🎬 *{title}*\n⏱️ Davomiyligi: {duration}",
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            f"🎬 *{title}*\n⏱️ Davomiyligi: {duration}\n\n🖼️ Ko'rish mavjud emas",
            parse_mode='Markdown'
        )

async def download_audio(query, context, video_info):
    """Download audio"""
    await query.edit_message_text("🎵 Audio (MP3) yuklanmoqda...")
    
    try:
        result = await download_youtube_audio(video_info['url'])
        if result and result.get('file_data'):
            await query.message.reply_audio(
                audio=result['file_data'],
                title=video_info.get('title', 'Audio'),
                performer='Yukla Pro',
                filename=result.get('filename', 'audio.mp3'),
                duration=video_info.get('duration_seconds', 0)
            )
            await query.message.delete()
        else:
            await query.edit_message_text("❌ Audio yuklab bo'lmadi")
    except Exception as e:
        await query.edit_message_text(f"❌ Xatolik: {str(e)[:60]}")

async def download_video_quality(query, context, video_info, quality):
    """Download video with selected quality"""
    await query.edit_message_text(f"📥 {quality} yuklanmoqda...")
    
    try:
        result = await download_youtube(video_info['url'], quality=quality)
        if result and result.get('file_data'):
            await query.message.reply_video(
                video=result['file_data'],
                caption=f"✅ Yuklandi: {video_info.get('title', 'Video')} ({quality})",
                supports_streaming=True,
                filename=result.get('filename', 'video.mp4')
            )
            await query.message.delete()
        else:
            await query.edit_message_text(f"❌ {quality} yuklab bo'lmadi")
    except Exception as e:
        await query.edit_message_text(f"❌ Xatolik: {str(e)[:60]}")