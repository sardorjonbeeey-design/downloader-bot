"""
URL download handlers with proper status feedback
"""
import logging
import asyncio
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

from config import config
from utils.validators import detect_url_type
from services.instagram import download_instagram
from services.tiktok import download_tiktok
from services.youtube import download_youtube, download_youtube_audio
from keyboards.inline import get_quality_keyboard
from utils.helpers import format_file_size, cleanup_file

logger = logging.getLogger(__name__)

async def update_status_message(msg, text, emoji="🔄"):
    """Update status message with animation"""
    animations = ["🔄", "⏳", "⌛", "⏰"]
    current = animations.index(emoji) if emoji in animations else 0
    next_emoji = animations[(current + 1) % len(animations)]
    await msg.edit_text(f"{next_emoji} {text}")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL input or music search"""
    text = update.message.text.strip()
    
    # Detect URL type
    url_type = detect_url_type(text)
    
    if url_type == 'music':
        from handlers.music import handle_music_search
        await handle_music_search(update, context)
        return
    
    # Show animated processing message
    status_msg = await update.message.reply_text(
        f"🔄 Processing {url_type.capitalize()} content..."
    )
    
    # Animate status
    animation_task = asyncio.create_task(animate_status(status_msg, url_type))
    
    try:
        # Simulate steps for better UX
        await asyncio.sleep(0.5)
        await status_msg.edit_text(f"⏳ Checking link...")
        await asyncio.sleep(0.5)
        
        if url_type == 'instagram':
            await status_msg.edit_text(f"⏳ Fetching Instagram content...")
            result = await download_instagram(text)
            
            if not result:
                await animation_task.cancel()
                await status_msg.edit_text(
                    "❌ *Instagram Download Failed*\n\n"
                    "• Post might be private\n"
                    "• Link might be invalid\n"
                    "• Instagram is blocking the request\n\n"
                    "💡 Try a different link or try again later.",
                    parse_mode='Markdown'
                )
                return
                
        elif url_type == 'tiktok':
            await status_msg.edit_text(f"⏳ Fetching TikTok content...")
            result = await download_tiktok(text)
            
            if not result:
                await animation_task.cancel()
                await status_msg.edit_text(
                    "❌ *TikTok Download Failed*\n\n"
                    "• Video might be private\n"
                    "• Link might be invalid\n"
                    "• TikTok is blocking the request\n\n"
                    "💡 Try a different link or try again later.",
                    parse_mode='Markdown'
                )
                return
                
        elif url_type == 'youtube':
            await status_msg.edit_text(f"⏳ Fetching YouTube video info...")
            result = await download_youtube(text)
            
            if not result:
                await animation_task.cancel()
                await status_msg.edit_text(
                    "❌ *YouTube Download Failed*\n\n"
                    "• Video might be private\n"
                    "• Link might be invalid\n"
                    "• YouTube is blocking the request\n\n"
                    "💡 Try a different link or try again later.",
                    parse_mode='Markdown'
                )
                return
            
            # For YouTube, show quality selection
            if 'qualities' in result:
                await animation_task.cancel()
                keyboard = get_quality_keyboard(result['qualities'], result['video_id'])
                await status_msg.delete()
                await update.message.reply_text(
                    f"✅ *Video Found!*\n\n"
                    f"🎬 *{result['title']}*\n"
                    f"📏 *Duration:* {result['duration']}\n"
                    f"📊 *Select quality to download:*",
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                context.user_data['youtube_video'] = result
                return
        else:
            await animation_task.cancel()
            await status_msg.edit_text("❌ Unsupported URL or platform")
            return
        
        # Send downloaded content
        if result and result.get('file_path'):
            await status_msg.edit_text(f"⏳ Preparing file for download...")
            
            file_path = result['file_path']
            
            # Check if file exists
            if not Path(file_path).exists():
                await animation_task.cancel()
                await status_msg.edit_text(
                    "❌ *File Not Found*\n\n"
                    "The download may have failed.\n"
                    "Please try again.",
                    parse_mode='Markdown'
                )
                return
                
            file_size = Path(file_path).stat().st_size
            
            # Check file size limit
            if file_size > config.MAX_FILE_SIZE * 1024 * 1024:
                await animation_task.cancel()
                await status_msg.edit_text(
                    f"❌ *File Too Large*\n\n"
                    f"Size: {format_file_size(file_size)}\n"
                    f"Maximum allowed: {config.MAX_FILE_SIZE}MB\n\n"
                    "💡 Try a different quality or format.",
                    parse_mode='Markdown'
                )
                cleanup_file(file_path)
                return
            
            # Send file with progress
            await status_msg.edit_text(f"📤 Sending file to Telegram...")
            
            caption = result.get('caption', '')
            try:
                if result.get('type') == 'video':
                    await update.message.reply_video(
                        video=open(file_path, 'rb'),
                        caption=f"✅ {caption}",
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
                        caption=f"✅ {caption}"
                    )
                else:
                    await update.message.reply_document(
                        document=open(file_path, 'rb'),
                        caption=f"✅ {caption}"
                    )
            except Exception as send_error:
                logger.error(f"Send error: {str(send_error)}")
                await animation_task.cancel()
                await status_msg.edit_text(
                    f"❌ *Failed to Send File*\n\n"
                    f"Error: {str(send_error)[:100]}\n\n"
                    "💡 The file might be too large or corrupted.",
                    parse_mode='Markdown'
                )
                cleanup_file(file_path)
                return
            
            # Clean up and success
            cleanup_file(file_path)
            await animation_task.cancel()
            await status_msg.delete()
            
    except Exception as e:
        logger.error(f"Download error: {str(e)}", exc_info=True)
        await animation_task.cancel()
        
        error_message = str(e)
        
        # User-friendly error messages
        if "Sign in to confirm" in error_message or "cookies" in error_message.lower():
            error_text = (
                "❌ *YouTube Authentication Required*\n\n"
                "The bot needs cookies to access YouTube.\n"
                "Please add a cookies.txt file to fix this."
            )
        elif "429" in error_message or "Too Many Requests" in error_message:
            error_text = (
                "⚠️ *Rate Limit Exceeded*\n\n"
                "The platform is receiving too many requests.\n"
                "Please wait a few minutes and try again."
            )
        elif "Private" in error_message or "private" in error_message:
            error_text = (
                "🔒 *Private Content*\n\n"
                "This content is private or restricted.\n"
                "Please use a public link."
            )
        else:
            error_text = (
                f"❌ *Download Failed*\n\n"
                f"Error: {error_message[:150]}\n\n"
                "💡 Try again or use a different link.\n"
                "If the problem persists, contact support."
            )
        
        await status_msg.edit_text(error_text, parse_mode='Markdown')

async def animate_status(msg, url_type):
    """Animate status message while processing"""
    animations = ["🔄", "⏳", "⌛", "⏰"]
    texts = [
        f"Processing {url_type.capitalize()} content...",
        f"Still working on it...",
        f"Almost there...",
        f"Finishing up..."
    ]
    
    i = 0
    while True:
        await asyncio.sleep(1.5)
        try:
            await msg.edit_text(f"{animations[i % len(animations)]} {texts[i % len(texts)]}")
            i += 1
        except:
            break

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
        await query.edit_message_text("❌ *Session Expired*\n\nPlease send the link again.", parse_mode='Markdown')
        return
    
    if action == 'quality':
        quality = parts[1]
        
        if quality == 'audio':
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
                else:
                    await query.edit_message_text(
                        "❌ *Audio Download Failed*\n\n"
                        "Could not extract audio from this video.",
                        parse_mode='Markdown'
                    )
            except Exception as e:
                logger.error(f"Audio download error: {str(e)}", exc_info=True)
                await query.edit_message_text(
                    f"❌ *Download Failed*\n\n{str(e)[:150]}",
                    parse_mode='Markdown'
                )
        else:
            # Download video with selected quality
            await query.edit_message_text(f"🔄 Downloading {quality}...")
            try:
                result = await download_youtube(video_info['url'], quality=quality)
                if result and result.get('file_path'):
                    file_path = result['file_path']
                    
                    # Send video
                    await query.message.reply_video(
                        video=open(file_path, 'rb'),
                        caption=f"✅ Downloaded: {video_info['title']}",
                        supports_streaming=True
                    )
                    
                    cleanup_file(file_path)
                    await query.message.delete()
                else:
                    await query.edit_message_text(
                        f"❌ *{quality} Download Failed*\n\n"
                        "Could not download this quality.\n"
                        "Please try a different quality.",
                        parse_mode='Markdown'
                    )
            except Exception as e:
                logger.error(f"Quality download error: {str(e)}", exc_info=True)
                await query.edit_message_text(
                    f"❌ *Download Failed*\n\n{str(e)[:150]}",
                    parse_mode='Markdown'
                )