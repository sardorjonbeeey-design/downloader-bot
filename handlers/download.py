"""
URL download handlers
"""
import logging
import asyncio
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import config
from utils.validators import detect_url_type
from services.downloader import download_content
from services.instagram import download_instagram
from services.tiktok import download_tiktok
from services.youtube import download_youtube, download_youtube_audio
from keyboards.inline import get_quality_keyboard
from utils.helpers import format_file_size, cleanup_file

logger = logging.getLogger(__name__)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL input or music search"""
    text = update.message.text.strip()
    
    # Detect URL type
    url_type = detect_url_type(text)
    
    if url_type == 'music':
        # Hand off to music handler
        from handlers.music import handle_music_search
        await handle_music_search(update, context)
        return
    
    # Show processing message
    status_msg = await update.message.reply_text(
        f"🔄 Processing {url_type.capitalize()} content..."
    )
    
    try:
        if url_type == 'instagram':
            result = await download_instagram(text)
        elif url_type == 'tiktok':
            result = await download_tiktok(text)
        elif url_type == 'youtube':
            result = await download_youtube(text)
            
            # For YouTube, show quality selection
            if result and 'qualities' in result:
                keyboard = get_quality_keyboard(result['qualities'], result['video_id'])
                await status_msg.delete()
                await update.message.reply_text(
                    f"🎬 *{result['title']}*\n\n"
                    f"📏 *Duration:* {result['duration']}\n"
                    f"📊 Select quality to download:",
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                # Store video info in context
                context.user_data['youtube_video'] = result
                return
        else:
            await status_msg.edit_text("❌ Unsupported URL or platform")
            return
        
        # Send downloaded content
        if result and result.get('file_path'):
            file_path = result['file_path']
            file_size = Path(file_path).stat().st_size
            
            # Check file size limit
            if file_size > config.MAX_FILE_SIZE * 1024 * 1024:
                await status_msg.edit_text(
                    f"❌ File too large: {format_file_size(file_size)}\n"
                    f"Maximum allowed: {config.MAX_FILE_SIZE}MB"
                )
                cleanup_file(file_path)
                return
            
            # Send file
            caption = result.get('caption', '')
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
                    performer=result.get('artist', 'Unknown')
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
            
            # Clean up
            cleanup_file(file_path)
            await status_msg.delete()
            
    except Exception as e:
        logger.error(f"Download error: {str(e)}", exc_info=True)
        await status_msg.edit_text(
            f"❌ An error occurred: {str(e)}\n"
            "Please try again or use /help for assistance."
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    parts = data.split('_')
    action = parts[0]
    video_id = parts[-1]
    
    # Get stored video info
    video_info = context.user_data.get('youtube_video', {})
    if not video_info or video_info.get('video_id') != video_id:
        await query.edit_message_text("❌ Session expired. Please send the link again.")
        return
    
    if action == 'quality':
        quality = parts[1]
        
        if quality == 'audio':
            # Download audio
            await query.edit_message_text("🎵 Downloading audio...")
            try:
                result = await download_youtube_audio(video_info['url'])
                if result and result.get('file_path'):
                    file_path = result['file_path']
                    await query.message.reply_audio(
                        audio=open(file_path, 'rb'),
                        title=video_info['title'],
                        performer='YouTube'
                    )
                    cleanup_file(file_path)
                    await query.message.delete()
            except Exception as e:
                logger.error(f"Audio download error: {str(e)}", exc_info=True)
                await query.edit_message_text(f"❌ Download failed: {str(e)}")
        else:
            # Download video with selected quality
            await query.edit_message_text(f"🔄 Downloading {quality}...")
            try:
                result = await download_youtube(video_info['url'], quality=quality)
                if result and result.get('file_path'):
                    file_path = result['file_path']
                    file_size = Path(file_path).stat().st_size
                    
                    # Send video
                    await query.message.reply_video(
                        video=open(file_path, 'rb'),
                        caption=f"✅ Downloaded: {video_info['title']}",
                        supports_streaming=True
                    )
                    
                    cleanup_file(file_path)
                    await query.message.delete()
            except Exception as e:
                logger.error(f"Quality download error: {str(e)}", exc_info=True)
                await query.edit_message_text(f"❌ Download failed: {str(e)}")