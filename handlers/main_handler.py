"""
Main Handler - Yukla Pro
ALL logic in ONE file. Update this when you need to fix anything.
"""
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import config
from services.instagram import download_instagram
from services.tiktok import download_tiktok
from services.youtube import download_youtube, download_youtube_audio
from services.pinterest import download_pinterest
from services.music import search_music, download_music
from services.cobalt import cobalt
from handlers.admin import stats_manager

logger = logging.getLogger(__name__)

# ============================================
# URL DETECTION
# ============================================

def detect_url_type(text: str) -> str:
    """Detect platform from URL"""
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
# START / HELP / INFO
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message"""
    welcome = (
        "🎯 *Yukla Pro*\n"
        "Universal Downloader Bot\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send me any link and I'll download it:\n\n"
        "📸 Instagram · Posts · Reels · Stories\n"
        "🎵 TikTok · Videos · Photos · Audio\n"
        "▶️ YouTube · Videos · Shorts · MP3\n"
        "📌 Pinterest · Images · Videos\n"
        "🎶 Music · Search by song name\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Just paste a link or type a song name.\n"
        "No commands needed.\n\n"
        "ℹ️ /help · /info · /stats (Admin)"
    )
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help message"""
    help_text = (
        "📖 *Yukla Pro Guide*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*How to use:*\n"
        "1. Copy any link\n"
        "2. Paste it here\n"
        "3. Wait for download\n\n"
        "*Supported platforms:*\n"
        "📸 Instagram · Posts · Reels · Stories\n"
        "🎵 TikTok · Videos · Photos\n"
        "▶️ YouTube · Videos · Shorts · MP3\n"
        "📌 Pinterest · Images · Videos\n"
        "🎶 Music · Search by song name\n\n"
        "*Tips:*\n"
        "• YouTube videos show quality options\n"
        "• Type song name for MP3 audio\n"
        "• Public content only\n"
        "• Max file size: 50MB (Telegram limit)\n\n"
        "/start · /info · /stats"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Info message"""
    info_text = (
        "ℹ️ *Yukla Pro*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Version · 2.0\n"
        "Status · Online\n\n"
        "*Supported:*\n"
        "Instagram · TikTok · YouTube · Pinterest\n\n"
        "*Features:*\n"
        "✅ Auto-detect links\n"
        "✅ Quality selection (YouTube)\n"
        "✅ MP3 audio extraction\n"
        "✅ Story download\n"
        "✅ Profile picture download\n"
        "✅ Admin analytics\n"
        "✅ No file storage (streams directly)\n\n"
        "Made with ❤️"
    )
    await update.message.reply_text(info_text, parse_mode='Markdown')

# ============================================
# MAIN URL HANDLER - ONE FUNCTION
# ============================================

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle ANY URL - All platforms in ONE function"""
    text = update.message.text.strip()
    url_type = detect_url_type(text)
    user_id = update.effective_user.id
    
    # Music search
    if url_type == 'music':
        await handle_music_search(update, context)
        return
    
    if url_type == 'unknown':
        await update.message.reply_text(
            "❌ Unsupported link or platform.\n\n"
            "Supported: Instagram · TikTok · YouTube · Pinterest"
        )
        return
    
    # Processing message
    status_msg = await update.message.reply_text(f"⬇️ Processing {url_type.capitalize()}...")
    
    try:
        result = None
        
        # ----- INSTAGRAM -----
        if url_type == 'instagram':
            result = await download_instagram(text)
            if result:
                stats_manager.add_download(user_id, 'instagram')
            else:
                await status_msg.edit_text(
                    "❌ Instagram download failed\n\n"
                    "• Post might be private\n"
                    "• Link might be invalid\n"
                    "• Try again later"
                )
                return
        
        # ----- TIKTOK -----
        elif url_type == 'tiktok':
            result = await download_tiktok(text)
            if result:
                stats_manager.add_download(user_id, 'tiktok')
            else:
                await status_msg.edit_text(
                    "❌ TikTok download failed\n\n"
                    "• Video might be private\n"
                    "• Link might be invalid\n"
                    "• Try again later"
                )
                return
        
        # ----- YOUTUBE -----
        elif url_type == 'youtube':
            result = await download_youtube(text)
            if not result:
                await status_msg.edit_text(
                    "❌ YouTube download failed\n\n"
                    "• Video might be private\n"
                    "• Link might be invalid\n"
                    "• YouTube may need cookies"
                )
                return
            
            # Show quality selection
            if 'qualities' in result:
                keyboard = get_quality_keyboard(result['qualities'], result['video_id'])
                await status_msg.delete()
                await update.message.reply_text(
                    f"🎬 *{result['title']}*\n"
                    f"⏱️ {result['duration']}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"Select quality:",
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                context.user_data['youtube_video'] = result
                stats_manager.add_download(user_id, 'youtube')
                return
        
        # ----- PINTEREST -----
        elif url_type == 'pinterest':
            result = await download_pinterest(text)
            if result:
                stats_manager.add_download(user_id, 'pinterest')
            else:
                await status_msg.edit_text(
                    "❌ Pinterest download failed\n\n"
                    "• Image/video might be private\n"
                    "• Link might be invalid"
                )
                return
        
        else:
            await status_msg.edit_text("❌ Unsupported platform")
            return
        
        # ----- SEND FILE (NO STORAGE) -----
        if result and result.get('file_data'):
            await status_msg.edit_text("⬇️ Sending...")
            
            file_data = result['file_data']
            filename = result.get('filename', 'download.mp4')
            file_type = result.get('type', 'document')
            caption = result.get('caption', '✅ Download complete')
            
            try:
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
                        performer=result.get('artist', 'Yukla Pro'),
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
            except Exception as send_error:
                await status_msg.edit_text(f"❌ Send failed: {str(send_error)[:80]}")
                return
            
            await status_msg.delete()
    
    except Exception as e:
        logger.error(f"Download error: {str(e)}", exc_info=True)
        await status_msg.edit_text(f"❌ Error: {str(e)[:100]}")

# ============================================
# MUSIC SEARCH - ONE FUNCTION
# ============================================

async def handle_music_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle music search - one function"""
    query = update.message.text.strip()
    
    status_msg = await update.message.reply_text(f"🔍 Searching \"{query}\"...")
    
    try:
        results = await search_music(query)
        
        if not results:
            await status_msg.edit_text(
                f"❌ No results found\n\n"
                f"\"{query}\"\n\n"
                "Try:\n"
                "• Different spelling\n"
                "• Artist + song name"
            )
            return
        
        result = results[0]
        await status_msg.delete()
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎵 Download MP3", callback_data=f"music_download_{result['id']}"),
                InlineKeyboardButton("▶️ Watch", url=result['url'])
            ]
        ])
        
        await update.message.reply_photo(
            photo=result['thumbnail'],
            caption=(
                f"🎵 *{result['title']}*\n"
                f"👤 Artist · {result['artist']}\n"
                f"⏱️ Duration · {result['duration']}\n\n"
                f"Select option:"
            ),
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        context.user_data['music_result'] = result
        stats_manager.add_download(update.effective_user.id, 'music')
        
    except Exception as e:
        logger.error(f"Music error: {str(e)}", exc_info=True)
        await status_msg.edit_text(f"❌ Error: {str(e)[:100]}")

async def handle_music_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle music download callback"""
    query = update.callback_query
    await query.answer()
    
    _, action, music_id = query.data.split('_')
    
    if action == 'download':
        result = context.user_data.get('music_result')
        
        if not result or result.get('id') != music_id:
            await query.edit_message_text("❌ Session expired. Search again.")
            return
        
        await query.edit_message_text("⬇️ Downloading MP3...")
        
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
                await query.edit_message_text(f"❌ {error or 'Download failed'}")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)[:60]}")

# ============================================
# YOUTUBE CALLBACK - ONE FUNCTION
# ============================================

async def handle_youtube_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle YouTube quality selection"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    parts = data.split('_')
    action = parts[0]
    video_id = parts[-1]
    
    video_info = context.user_data.get('youtube_video', {})
    if not video_info or video_info.get('video_id') != video_id:
        await query.edit_message_text("❌ Session expired. Send the link again.")
        return
    
    if action == 'quality':
        quality = parts[1]
        
        if quality == 'audio':
            await query.edit_message_text("🎵 Downloading audio...")
            try:
                result = await download_youtube_audio(video_info['url'])
                if result and result.get('file_data'):
                    await query.message.reply_audio(
                        audio=result['file_data'],
                        title=video_info['title'],
                        performer='Yukla Pro',
                        filename=result.get('filename', 'audio.mp3')
                    )
                    await query.message.delete()
                else:
                    await query.edit_message_text("❌ Audio download failed")
            except Exception as e:
                await query.edit_message_text(f"❌ Error: {str(e)[:60]}")
        else:
            await query.edit_message_text(f"⬇️ Downloading {quality}...")
            try:
                result = await download_youtube(video_info['url'], quality=quality)
                if result and result.get('file_data'):
                    await query.message.reply_video(
                        video=result['file_data'],
                        caption=f"✅ Downloaded: {video_info['title']}",
                        supports_streaming=True,
                        filename=result.get('filename', 'video.mp4')
                    )
                    await query.message.delete()
                else:
                    await query.edit_message_text(f"❌ {quality} download failed")
            except Exception as e:
                await query.edit_message_text(f"❌ Error: {str(e)[:60]}")

# ============================================
# KEYBOARD - ONE FUNCTION
# ============================================

def get_quality_keyboard(qualities: dict, video_id: str) -> InlineKeyboardMarkup:
    """Create quality selection keyboard"""
    keyboard = []
    
    for quality_key, quality_data in qualities.items():
        label = quality_data['label']
        size = quality_data.get('size', '')
        button_text = f"{label} {size}" if size else label
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"quality_{quality_key}_{video_id}")
        ])
    
    keyboard.append([
        InlineKeyboardButton("🎵 MP3 Audio", callback_data=f"quality_audio_{video_id}")
    ])
    
    return InlineKeyboardMarkup(keyboard)