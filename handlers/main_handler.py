"""
Main Handler - Yukla Pro
ONE FILE with ALL logic - Complete working code
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

logger = logging.getLogger(__name__)

# ============================================
# 1. URL DETECTION
# ============================================

def detect_url_type(text: str) -> str:
    text = text.lower()
    if 'instagram.com' in text or 'instagr.am' in text:
        return 'instagram'
    if 'tiktok.com' in text or 'vm.tiktok.com' in text:
        return 'tiktok'
    if 'youtube.com' in text or 'youtu.be' in text:
        return 'youtube'
    if 'pinterest.com' in text:
        return 'pinterest'
    if re.search(r'\b\w+\s+\w+\b', text) and not re.search(r'https?://', text):
        return 'music'
    return 'unknown'

# ============================================
# 2. START / HELP / INFO
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "🎯 *Yukla Pro*\n"
        "Universal Yuklab Oluvchi Bot\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Menga har qanday havolani yuboring:\n\n"
        "📸 Instagram · Postlar · Reels · Story\n"
        "🎵 TikTok · Videolar · Rasmlar\n"
        "▶️ YouTube · Videolar · Shorts · MP3\n"
        "📌 Pinterest · Rasmlar · Videolar\n"
        "🎶 Music · Qo'shiq nomi bilan qidirish\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Havolani yoki qo'shiq nomini yozing.\n"
        "Hech qanday buyruq kerak emas.\n\n"
        "ℹ️ /help · /info · /stats (Admin)"
    )
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 *Yukla Pro Qo'llanma*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*Qanday ishlatish:*\n"
        "1. Havolani nusxalang\n"
        "2. Shu yerga yuboring\n"
        "3. Yuklab olishni kuting\n\n"
        "*Qo'llab-quvvatlanadigan platformalar:*\n"
        "📸 Instagram · Postlar · Reels · Story\n"
        "🎵 TikTok · Videolar · Rasmlar\n"
        "▶️ YouTube · Videolar · Shorts · MP3\n"
        "📌 Pinterest · Rasmlar · Videolar\n"
        "🎶 Music · Qo'shiq nomi bilan qidirish\n\n"
        "*Maslahatlar:*\n"
        "• YouTube: sifatni tanlang (144p dan 1080p gacha)\n"
        "• Audio uchun qo'shiq nomini yozing\n"
        "• Faqat ochiq kontent\n"
        "• Maksimal fayl hajmi: 50MB\n\n"
        "/start · /info · /stats"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = (
        "ℹ️ *Yukla Pro*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Versiya · 2.0\n"
        "Holat · Faol\n\n"
        "*Qo'llab-quvvatlaydi:*\n"
        "Instagram · TikTok · YouTube · Pinterest\n\n"
        "*Xususiyatlar:*\n"
        "✅ Avtomatik link aniqlash\n"
        "✅ Sifat tanlash (YouTube)\n"
        "✅ MP3 audio olish\n"
        "✅ Story saqlash\n"
        "✅ Profil rasmi olish\n"
        "✅ Admin statistikasi\n"
        "✅ Fayl saqlamasdan to'g'ridan-to'g'ri yuklash\n\n"
        "❤️ bilan yaratilgan"
    )
    await update.message.reply_text(info_text, parse_mode='Markdown')

# ============================================
# 3. YOUTUBE FUNCTIONS
# ============================================

def build_youtube_keyboard(result: dict, video_id: str) -> InlineKeyboardMarkup:
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

async def handle_youtube(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE, status_msg):
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
    if 'qualities' in result:
        try:
            await status_msg.delete()
        except Exception:
            pass
        keyboard = build_youtube_keyboard(result, result.get('video_id', 'unknown'))
        title = result.get('title', "Noma'lum")
        duration = result.get('duration', "Noma'lum")
        caption = (
            f"▶️ *YouTube*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎬 *{title}*\n"
            f"⏱️ Davomiyligi: {duration}\n\n"
            f"📥 *Sifatni tanlang:*\n"
            f"• Video: MP4\n"
            f"• Audio: MP3 (192kbps)"
        )
        if result.get('thumbnail'):
            await update.message.reply_photo(
                photo=result['thumbnail'],
                caption=caption,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(caption, reply_markup=keyboard, parse_mode='Markdown')
        context.user_data['youtube_video'] = result
        stats_manager.add_download(user_id, 'youtube')
        return None
    return result

async def youtube_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
    
    data = query.data
    parts = data.split('_')
    if len(parts) < 3:
        try:
            await query.edit_message_text("❌ Noto'g'ri tanlov")
        except Exception:
            pass
        return
    
    action = parts[1]
    video_id = parts[2]
    video_info = context.user_data.get('youtube_video', {})
    if not video_info or video_info.get('video_id') != video_id:
        try:
            await query.edit_message_text("❌ Vaqt tugadi. Havolani qayta yuboring.")
        except Exception:
            pass
        return
    
    if action == 'preview':
        thumbnail = video_info.get('thumbnail')
        title = video_info.get('title', 'Video')
        duration = video_info.get('duration', "Noma'lum")
        if thumbnail:
            try:
                await query.edit_message_caption(caption=f"🎬 *{title}*\n⏱️ Davomiyligi: {duration}", parse_mode='Markdown')
            except Exception:
                pass
        else:
            try:
                await query.edit_message_text(f"🎬 *{title}*\n⏱️ Davomiyligi: {duration}\n\n🖼️ Ko'rish mavjud emas", parse_mode='Markdown')
            except Exception:
                pass
        return
    
    if action == 'audio':
        try:
            await query.edit_message_text("🎵 Audio (MP3) yuklanmoqda...")
        except Exception:
            pass
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
                try:
                    await query.message.delete()
                except Exception:
                    pass
            else:
                try:
                    await query.edit_message_text("❌ Audio yuklab bo'lmadi")
                except Exception:
                    pass
        except Exception as e:
            try:
                await query.edit_message_text(f"❌ Xatolik: {str(e)[:60]}")
            except Exception:
                pass
        return
    
    try:
        await query.edit_message_text(f"📥 {action} yuklanmoqda...")
    except Exception:
        pass
    try:
        result = await download_youtube(video_info['url'], quality=action)
        if result and result.get('file_data'):
            await query.message.reply_video(
                video=result['file_data'],
                caption=f"✅ Yuklandi: {video_info.get('title', 'Video')} ({action})",
                supports_streaming=True,
                filename=result.get('filename', 'video.mp4')
            )
            try:
                await query.message.delete()
            except Exception:
                pass
        else:
            try:
                await query.edit_message_text(f"❌ {action} yuklab bo'lmadi")
            except Exception:
                pass
    except Exception as e:
        try:
            await query.edit_message_text(f"❌ Xatolik: {str(e)[:60]}")
        except Exception:
            pass

# ============================================
# 4. INSTAGRAM
# ============================================

async def handle_instagram(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE, status_msg):
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

# ============================================
# 5. TIKTOK
# ============================================

async def handle_tiktok(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE, status_msg):
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

# ============================================
# 6. PINTEREST
# ============================================

async def handle_pinterest(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE, status_msg):
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

# ============================================
# 7. MUSIC - TEXT ONLY (NO THUMBNAIL)
# ============================================

async def handle_music_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle music search - text only, no thumbnail"""
    query = update.message.text.strip()
    status_msg = await update.message.reply_text(f"🔍 \"{query}\" qidirilmoqda...")
    
    try:
        results = await search_music(query)
        if not results:
            try:
                await status_msg.edit_text(
                    f"❌ Natija topilmadi\n\n"
                    f"\"{query}\"\n\n"
                    "Urinib ko'ring:\n"
                    "• Boshqa imlo\n"
                    "• Artist + qo'shiq nomi"
                )
            except Exception:
                await update.message.reply_text(
                    f"❌ Natija topilmadi\n\n"
                    f"\"{query}\"\n\n"
                    "Urinib ko'ring:\n"
                    "• Boshqa imlo\n"
                    "• Artist + qo'shiq nomi"
                )
            return
        
        result = results[0]
        try:
            await status_msg.delete()
        except Exception:
            pass
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎵 MP3 Yuklab olish", callback_data=f"music_download_{result['id']}"),
                InlineKeyboardButton("▶️ Ko'rish", url=result['url'])
            ]
        ])
        
        # TEXT ONLY - No photo, no thumbnail
        await update.message.reply_text(
            f"🎵 *{result['title']}*\n"
            f"👤 Artist · {result['artist']}\n"
            f"⏱️ Davomiyligi · {result['duration']}\n\n"
            f"📥 Tanlang:",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        context.user_data['music_result'] = result
        stats_manager.add_download(update.effective_user.id, 'music')
        
    except Exception as e:
        logger.error(f"Music xatolik: {str(e)}", exc_info=True)
        try:
            await status_msg.edit_text(f"❌ Xatolik: {str(e)[:100]}")
        except Exception:
            await update.message.reply_text(f"❌ Xatolik: {str(e)[:100]}")

async def handle_music_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    try:
        await query.answer()
    except Exception:
        pass
    
    try:
        _, action, music_id = query.data.split('_')
    except ValueError:
        try:
            await query.edit_message_text("❌ Xatolik yuz berdi.")
        except Exception:
            pass
        return
    
    if action == 'download':
        result = context.user_data.get('music_result')
        if not result or result.get('id') != music_id:
            try:
                await query.edit_message_text("❌ Vaqt tugadi. Qayta qidiring.")
            except Exception:
                pass
            return
        
        try:
            await query.edit_message_text("🎵 MP3 yuklanmoqda...")
        except Exception:
            pass
        
        try:
            file_data, filename, error = await download_music(result['url'])
            if file_data:
                try:
                    await query.message.reply_audio(
                        audio=file_data,
                        title=result['title'],
                        performer=result['artist'],
                        duration=result.get('duration_seconds', 0),
                        filename=filename
                    )
                except Exception as send_error:
                    await query.message.reply_text(f"❌ Yuborish xatosi: {str(send_error)[:60]}")
                
                try:
                    await query.message.delete()
                except Exception:
                    pass
            else:
                error_msg = error or "Yuklab bo'lmadi"
                try:
                    await query.edit_message_text(f"❌ {error_msg}")
                except Exception:
                    await query.message.reply_text(f"❌ {error_msg}")
        except Exception as e:
            try:
                await query.edit_message_text(f"❌ Xatolik: {str(e)[:60]}")
            except Exception:
                await query.message.reply_text(f"❌ Xatolik: {str(e)[:60]}")

# ============================================
# 8. SEND FILE
# ============================================

async def send_file(update, status_msg, result):
    try:
        await status_msg.edit_text("⬇️ Yuborilmoqda...")
    except Exception:
        pass
    
    try:
        file_data = result['file_data']
        filename = result.get('filename', 'download.mp4')
        file_type = result.get('type', 'document')
        caption = result.get('caption', '✅ Yuklandi')
        
        if file_type == 'video':
            await update.message.reply_video(
                video=file_data,
                caption=caption,
                supports_streaming=True,
                filename=filename
            )
        elif file_type == 'audio':
            await update.message.reply_audio(
                audio=file_data,
                title=result.get('title', 'Audio'),
                performer='Yukla Pro',
                filename=filename
            )
        elif file_type == 'photo':
            await update.message.reply_photo(
                photo=file_data,
                caption=caption
            )
        else:
            await update.message.reply_document(
                document=file_data,
                caption=caption,
                filename=filename
            )
        
        try:
            await status_msg.delete()
        except Exception:
            pass
            
    except Exception as e:
        try:
            await status_msg.edit_text(f"❌ Yuborish xatosi: {str(e)[:80]}")
        except Exception:
            await update.message.reply_text(f"❌ Yuborish xatosi: {str(e)[:80]}")

# ============================================
# 9. MAIN URL HANDLER
# ============================================

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    url_type = detect_url_type(text)
    
    if url_type == 'unknown':
        await update.message.reply_text(
            "❌ Qo'llab-quvvatlanmaydigan link.\n\n"
            "Qo'llab-quvvatlanadi: Instagram · TikTok · YouTube · Pinterest"
        )
        return
    
    status_msg = await update.message.reply_text(f"🔄 {url_type.capitalize()} qayta ishlanmoqda...")
    
    try:
        if url_type == 'instagram':
            result = await handle_instagram(text, update, context, status_msg)
        elif url_type == 'tiktok':
            result = await handle_tiktok(text, update, context, status_msg)
        elif url_type == 'youtube':
            result = await handle_youtube(text, update, context, status_msg)
            if result is None:
                return
        elif url_type == 'pinterest':
            result = await handle_pinterest(text, update, context, status_msg)
        elif url_type == 'music':
            await handle_music_search(update, context)
            return
        else:
            await status_msg.edit_text("❌ Qo'llab-quvvatlanmaydi")
            return
        
        if result and result.get('file_data'):
            await send_file(update, status_msg, result)
        elif result is None:
            pass
        else:
            await status_msg.edit_text("❌ Yuklab bo'lmadi")
            
    except Exception as e:
        logger.error(f"Handle URL error: {str(e)}", exc_info=True)
        try:
            await status_msg.edit_text(f"❌ Xatolik: {str(e)[:100]}")
        except Exception:
            await update.message.reply_text(f"❌ Xatolik: {str(e)[:100]}")