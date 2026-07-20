"""
Music search and download handlers - Yukla Pro Audio
"""
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.music import search_music, download_music
from utils.helpers import cleanup_file

logger = logging.getLogger(__name__)

async def animate_search(msg, query):
    """Animate search - Minimal"""
    animations = ["·", "··", "···"]
    texts = [
        f"Searching for \"{query}\"",
        f"Finding audio",
        f"Almost ready"
    ]
    
    i = 0
    while True:
        await asyncio.sleep(0.8)
        try:
            await msg.edit_text(f"{animations[i % len(animations)]} {texts[i % len(texts)]}")
            i += 1
        except:
            break

async def handle_music_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle music/audio search"""
    query_text = update.message.text.strip()
    
    status_msg = await update.message.reply_text(
        f"· Searching for \"{query_text}\"..."
    )
    
    animation_task = asyncio.create_task(animate_search(status_msg, query_text))
    
    try:
        results = await search_music(query_text)
        
        if not results:
            animation_task.cancel()
            await status_msg.edit_text(
                f"✗ No results found\n\n"
                f"\"{query_text}\"\n\n"
                "Try:\n"
                "· Different spelling\n"
                "· Artist + song name\n"
                "· Shorter query"
            )
            return
        
        result = results[0]
        animation_task.cancel()
        await status_msg.delete()
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎧 Download MP3", callback_data=f"music_download_{result['id']}"),
                InlineKeyboardButton("▶️ Watch", url=result['url'])
            ]
        ])
        
        await update.message.reply_photo(
            photo=result['thumbnail'],
            caption=(
                f"✓ **{result['title']}**\n\n"
                f"Artist · {result['artist']}\n"
                f"Duration · {result['duration']}\n\n"
                f"Select an option:"
            ),
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        context.user_data['music_result'] = result
        
    except Exception as e:
        logger.error(f"Music search error: {str(e)}", exc_info=True)
        animation_task.cancel()
        await status_msg.edit_text(f"✗ Search failed\n\n{str(e)[:100]}")

async def handle_music_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle music callback queries"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    _, action, music_id = data.split('_')
    
    if action == 'download':
        result = context.user_data.get('music_result')
        
        if not result or result.get('id') != music_id:
            await query.edit_message_text("✗ Session expired\n\nSearch again.")
            return
        
        await query.edit_message_text("· Downloading MP3...")
        
        try:
            file_path = await download_music(result['url'])
            
            if file_path:
                await query.message.reply_audio(
                    audio=open(file_path, 'rb'),
                    title=result['title'],
                    performer=result['artist'],
                    duration=result.get('duration_seconds', 0)
                )
                cleanup_file(file_path)
                await query.message.delete()
            else:
                await query.edit_message_text("✗ MP3 download failed")
                
        except Exception as e:
            logger.error(f"Music download error: {str(e)}", exc_info=True)
            await query.edit_message_text(f"✗ Error: {str(e)[:50]}")