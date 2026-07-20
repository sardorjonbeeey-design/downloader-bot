"""
URL download handlers - Yukla Pro Modern Interface
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

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL input - Yukla Pro"""
    text = update.message.text.strip()
    url_type = detect_url_type(text)
    
    if url_type == 'music':
        from handlers.music import handle_music_search
        await handle_music_search(update, context)
        return
    
    # Clean status message
    status_msg = await update.message.reply_text(
        f"⬇️ Processing {url_type.capitalize()}..."
    )
    
    try:
        if url_type == 'instagram':
            result = await download_instagram(text)
            if not result:
                await status_msg.edit_text(
                    "❌ Could not download Instagram content\n\n"
                    "• Make sure the post is public\n"
                    "• Check if the link is correct\n"
                    "• Try again in a few minutes\n\n"
                    "💡 If this keeps happening, the post might be age-restricted."
                )
                return
                
        elif url_type == 'tiktok':
            result = await download_tiktok(text)
            if not result:
                await status_msg.edit_text(
                    "❌ Could not download TikTok content\n\n"
                    "• Make sure the video is public\n"
                    "• Check if the link is correct\n\n"
                    "💡 Try again in a few minutes."
                )
                return
                
        elif url_type == 'youtube':
            await status_msg.edit_text("⬇️ Fetching YouTube video...")
            result = await download_youtube(text)
            if not result:
                await status_msg.edit_text(
                    "❌ Could not download YouTube video\n\n"
                    "• Make sure the video is public\n"
                    "• Check if the link is correct\n\n"
                    "💡 YouTube may require cookies for this video."
                )
                return
            
            if 'qualities' in result:
                keyboard = get_quality_keyboard(result['qualities'], result['video_id'])
                await status_msg.delete()
                await update.message.reply_text(
                    f"🎬 {result['title']}\n\n"
                    f"⏱️ {result['duration']}\n"
                    f"───────────\n"
                    f"Select quality:",
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                context.user_data['youtube_video'] = result
                return
        else:
            await status_msg.edit_text("❌ Unsupported platform")
            return
        
        # Send downloaded content
        if result and result.get('file_path'):
            file_path = result['file_path']
            
            if not Path(file_path).exists():
                await status_msg.edit_text("❌ File not found")
                return
                
            file_size = Path(file_path).stat().st_size
            
            if file_size > config.MAX_FILE_SIZE * 1024 * 1024:
                await status_msg.edit_text(
                    f"❌ File too large\n\n"
                    f"Size: {format_file_size(file_size)}\n"
                    f"Max: {config.MAX_FILE_SIZE}MB"
                )
                cleanup_file(file_path)
                return
            
            await status_msg.edit_text("⬇️ Sending...")
            
            try:
                if result.get('type') == 'video':
                    await update.message.reply_video(
                        video=open(file_path, 'rb'),
                        caption=f"✅ {result.get('caption', 'Download complete')}",
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
                        caption=f"✅ {result.get('caption', 'Download complete')}"
                    )
                else:
                    await update.message.reply_document(
                        document=open(file_path, 'rb'),
                        caption=f"✅ {result.get('caption', 'Download complete')}"
                    )
            except Exception as send_error:
                await status_msg.edit_text(f"❌ Send failed: {str(send_error)[:80]}")
                cleanup_file(file_path)
                return
            
            cleanup_file(file_path)
            await status_msg.delete()
            
    except Exception as e:
        logger.error(f"Download error: {str(e)}", exc_info=True)
        error_text = str(e)
        
        if "cookies" in error_text.lower():
            msg = "❌ YouTube needs cookies\n\nAdd cookies.txt to enable YouTube downloads."
        elif "429" in error_text:
            msg = "⚠️ Too many requests\n\nPlease wait and try again."
        else:
            msg = f"❌ Something went wrong\n\n{error_text[:100]}"
        
        await status_msg.edit_text(msg)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    parts = data.split('_')
    action = parts[0]
    video_id = parts[-1]
    
    video_info = context.user_data.get('youtube_video', {})
    if not video_info or video_info.get('video_id') != video_id:
        await query.edit_message_text("❌ Session expired\n\nPlease send the link again.")
        return
    
    if action == 'quality':
        quality = parts[1]
        
        if quality == 'audio':
            await query.edit_message_text("⬇️ Downloading audio...")
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
                    await query.edit_message_text("❌ Audio download failed")
            except Exception as e:
                await query.edit_message_text(f"❌ Error: {str(e)[:60]}")
        else:
            await query.edit_message_text(f"⬇️ Downloading {quality}...")
            try:
                result = await download_youtube(video_info['url'], quality=quality)
                if result and result.get('file_path'):
                    file_path = result['file_path']
                    await query.message.reply_video(
                        video=open(file_path, 'rb'),
                        caption=f"✅ Downloaded: {video_info['title']}",
                        supports_streaming=True
                    )
                    cleanup_file(file_path)
                    await query.message.delete()
                else:
                    await query.edit_message_text(f"❌ {quality} download failed")
            except Exception as e:
                await query.edit_message_text(f"❌ Error: {str(e)[:60]}")