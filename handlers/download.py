"""
URL download handlers - Yukla Pro Interface
"""
import logging
import asyncio
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import config
from utils.validators import detect_url_type
from services.instagram import download_instagram
from services.tiktok import download_tiktok
from services.youtube import download_youtube, download_youtube_audio
from keyboards.inline import get_quality_keyboard
from utils.helpers import format_file_size, cleanup_file

logger = logging.getLogger(__name__)

async def animate_status(msg, url_type):
    """Minimal animation for Yukla Pro"""
    animations = ["·", "··", "···"]
    texts = [
        f"Processing {url_type.capitalize()}",
        f"Downloading from {url_type.capitalize()}",
        f"Preparing file"
    ]
    
    i = 0
    while True:
        await asyncio.sleep(0.8)
        try:
            await msg.edit_text(f"{animations[i % len(animations)]} {texts[i % len(texts)]}")
            i += 1
        except:
            break

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL input - Yukla Pro"""
    text = update.message.text.strip()
    url_type = detect_url_type(text)
    
    # Music search (YouTube Audio only)
    if url_type == 'music':
        from handlers.music import handle_music_search
        await handle_music_search(update, context)
        return
    
    # Processing message
    status_msg = await update.message.reply_text(
        f"· Processing {url_type.capitalize()}..."
    )
    
    animation_task = asyncio.create_task(animate_status(status_msg, url_type))
    
    try:
        if url_type == 'instagram':
            result = await download_instagram(text)
            if not result:
                animation_task.cancel()
                await status_msg.edit_text(
                    "✗ Instagram download failed\n\n"
                    "· Private content\n"
                    "· Invalid link\n\n"
                    "Try a different link."
                )
                return
                
        elif url_type == 'tiktok':
            result = await download_tiktok(text)
            if not result:
                animation_task.cancel()
                await status_msg.edit_text(
                    "✗ TikTok download failed\n\n"
                    "· Private video\n"
                    "· Invalid link\n\n"
                    "Try a different link."
                )
                return
                
        elif url_type == 'youtube':
            result = await download_youtube(text)
            if not result:
                animation_task.cancel()
                await status_msg.edit_text(
                    "✗ YouTube download failed\n\n"
                    "· Private video\n"
                    "· Invalid link\n\n"
                    "Try a different link."
                )
                return
            
            # YouTube quality selection
            if 'qualities' in result:
                animation_task.cancel()
                keyboard = get_quality_keyboard(result['qualities'], result['video_id'])
                await status_msg.delete()
                
                quality_msg = (
                    f"✓ **{result['title']}**\n\n"
                    f"Duration · {result['duration']}\n"
                    f"Select quality to download:"
                )
                await update.message.reply_text(
                    quality_msg,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                context.user_data['youtube_video'] = result
                return
        else:
            animation_task.cancel()
            await status_msg.edit_text("✗ Unsupported platform")
            return
        
        # Send downloaded content
        if result and result.get('file_path'):
            file_path = result['file_path']
            
            if not Path(file_path).exists():
                animation_task.cancel()
                await status_msg.edit_text("✗ File not found")
                return
                
            file_size = Path(file_path).stat().st_size
            
            if file_size > config.MAX_FILE_SIZE * 1024 * 1024:
                animation_task.cancel()
                await status_msg.edit_text(
                    f"✗ File too large\n\n"
                    f"Size · {format_file_size(file_size)}\n"
                    f"Max · {config.MAX_FILE_SIZE}MB"
                )
                cleanup_file(file_path)
                return
            
            await status_msg.edit_text("· Sending file...")
            
            caption = result.get('caption', '✓ Download complete')
            try:
                if result.get('type') == 'video':
                    await update.message.reply_video(
                        video=open(file_path, 'rb'),
                        caption=caption,
                        supports_streaming=True
                    )
                elif result.get('type') == 'audio':
                    await update.message.reply_audio(
                        audio=open(file_path, 'rb'),
                        title=result.get('title', 'Audio'),
                        performer=result.get('artist', 'Yukla Pro')
                    )
                elif result.get('type') == 'photo':
                    await update.message.reply_photo(
                        photo=open(file_path, 'rb'),
                        caption=caption
                    )
                else:
                    await update.message.reply_document(
                        document=open(file_path, 'rb'),
                        caption=caption
                    )
            except Exception as send_error:
                logger.error(f"Send error: {str(send_error)}")
                animation_task.cancel()
                await status_msg.edit_text(f"✗ Send failed: {str(send_error)[:50]}")
                cleanup_file(file_path)
                return
            
            cleanup_file(file_path)
            animation_task.cancel()
            await status_msg.delete()
            
    except Exception as e:
        logger.error(f"Download error: {str(e)}", exc_info=True)
        animation_task.cancel()
        
        error_message = str(e)
        if "cookies" in error_message.lower():
            error_text = "✗ Authentication required\n\nAdd cookies.txt for YouTube."
        elif "429" in error_message:
            error_text = "⚠️ Rate limit\n\nWait a moment and try again."
        elif "Private" in error_message:
            error_text = "✗ Private content\n\nUse a public link."
        else:
            error_text = f"✗ Error\n\n{error_message[:100]}"
        
        await status_msg.edit_text(error_text)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries - Yukla Pro"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    parts = data.split('_')
    action = parts[0]
    video_id = parts[-1]
    
    video_info = context.user_data.get('youtube_video', {})
    if not video_info or video_info.get('video_id') != video_id:
        await query.edit_message_text("✗ Session expired\n\nSend the link again.")
        return
    
    if action == 'quality':
        quality = parts[1]
        
        if quality == 'audio':
            await query.edit_message_text("· Downloading audio...")
            try:
                result = await download_youtube_audio(video_info['url'])
                if result and result.get('file_path'):
                    file_path = result['file_path']
                    await query.message.reply_audio(
                        audio=open(file_path, 'rb'),
                        title=video_info['title'],
                        performer='Yukla Pro'
                    )
                    cleanup_file(file_path)
                    await query.message.delete()
                else:
                    await query.edit_message_text("✗ Audio download failed")
            except Exception as e:
                logger.error(f"Audio download error: {str(e)}", exc_info=True)
                await query.edit_message_text(f"✗ Error: {str(e)[:50]}")
        else:
            await query.edit_message_text(f"· Downloading {quality}...")
            try:
                result = await download_youtube(video_info['url'], quality=quality)
                if result and result.get('file_path'):
                    file_path = result['file_path']
                    await query.message.reply_video(
                        video=open(file_path, 'rb'),
                        caption=f"✓ Downloaded: {video_info['title']}",
                        supports_streaming=True
                    )
                    cleanup_file(file_path)
                    await query.message.delete()
                else:
                    await query.edit_message_text(f"✗ {quality} download failed")
            except Exception as e:
                logger.error(f"Quality download error: {str(e)}", exc_info=True)
                await query.edit_message_text(f"✗ Error: {str(e)[:50]}")