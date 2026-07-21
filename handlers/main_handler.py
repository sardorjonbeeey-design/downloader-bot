"""
Main Handler - Yukla Pro
FAQAT YO'NALTIRISH - Boshqa fayllarni chaqiradi
"""
import logging
import re
from telegram import Update
from telegram.ext import ContextTypes

from handlers.instagram import handle_instagram
from handlers.tiktok import handle_tiktok
from handlers.youtube import handle_youtube, youtube_callback_handler
from handlers.pinterest import handle_pinterest
from handlers.music import handle_music_search, handle_music_callback
from handlers.admin import stats_manager

logger = logging.getLogger(__name__)

def detect_url_type(text: str) -> str:
    """Platformani aniqlash"""
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
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
    """Yordam komandasi"""
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
    """Ma'lumot komandasi"""
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

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """BARCHA linklarni boshqarish - FAQAT YO'NALTIRISH"""
    text = update.message.text.strip()
    url_type = detect_url_type(text)
    
    if url_type == 'unknown':
        await update.message.reply_text(
            "❌ Qo'llab-quvvatlanmaydigan link.\n\n"
            "Qo'llab-quvvatlanadi: Instagram · TikTok · YouTube · Pinterest"
        )
        return
    
    # Yuklab olish holati
    status_msg = await update.message.reply_text(f"🔄 {url_type.capitalize()} qayta ishlanmoqda...")
    
    # Platformaga yo'naltirish
    if url_type == 'instagram':
        result = await handle_instagram(text, update, context, status_msg)
    elif url_type == 'tiktok':
        result = await handle_tiktok(text, update, context, status_msg)
    elif url_type == 'youtube':
        result = await handle_youtube(text, update, context, status_msg)
        if result is None:
            return  # YouTube o'zini boshqaradi
    elif url_type == 'pinterest':
        result = await handle_pinterest(text, update, context, status_msg)
    elif url_type == 'music':
        await handle_music_search(update, context)
        return
    else:
        await status_msg.edit_text("❌ Qo'llab-quvvatlanmaydi")
        return
    
    # Natijani yuborish
    if result and result.get('file_data'):
        await send_file(update, status_msg, result)
    elif result is None:
        pass  # Xatolik allaqachon ko'rsatilgan
    else:
        await status_msg.edit_text("❌ Yuklab bo'lmadi")

async def send_file(update, status_msg, result):
    """Faylni yuborish"""
    try:
        await status_msg.edit_text("⬇️ Yuborilmoqda...")
        
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
        
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Yuborish xatosi: {str(e)[:80]}")