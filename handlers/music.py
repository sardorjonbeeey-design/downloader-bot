"""
Music search and download handlers
"""
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.music import search_music, download_music
from utils.helpers import cleanup_file

logger = logging.getLogger(__name__)

async def handle_music_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle music search query"""
    query_text = update.message.text.strip()
    
    # Show animated searching message
    status_msg = await update.message.reply_text(
        f"🔍 Searching for \"{query_text}\"..."
    )
    
    # Animate search
    animation_task = asyncio.create_task(animate_search(status_msg, query_text))
    
    try:
        results = await search_music(query_text)
        
        if not results:
            await animation_task.cancel()
            await status_msg.edit_text(
                f"❌ *No Results Found*\n\n"
                f"Search: \"{query_text}\"\n\n"
                "💡 Tips:\n"
                "• Try a different spelling\n"
                "• Use artist + song name\n"
                "• Try a shorter query\n"
                "• Use English search terms",
                parse_mode='Markdown'
            )
            return
        
        # Show first result (best match)
        result = results[0]
        
        await animation_task.cancel()
        await status_msg.delete()
        
        # Create buttons
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎵 Download MP3", callback_data=f"music_download_{result['id']}"),
                InlineKeyboardButton("▶️ Watch on YouTube", url=result['url'])
            ]
        ])
        
        # Send music info
        await update.message.reply_photo(
            photo=result['thumbnail'],
            caption=(
                f"✅ *Found Song!*\n\n"
                f"🎵 *{result['title']}*\n"
                f"👤 *Artist:* {result['artist']}\n"
                f"⏱️ *Duration:* {result['duration']}\n\n"
                f"📌 *Select an option below:*"
            ),
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        # Store result for later use
        context.user_data['music_result'] = result
        
    except Exception as e:
        logger.error(f"Music search error: {str(e)}", exc_info=True)
        await animation_task.cancel()
        await status_msg.edit_text(
            f"❌ *Search Failed*\n\n"
            f"Error: {str(e)[:150]}\n\n"
            "💡 Please try again with a different search term.",
            parse_mode='Markdown'
        )

async def animate_search(msg, query):
    """Animate search message"""
    animations = ["🔍", "📀", "🎵", "🎶"]
    texts = [
        f"Searching for \"{query}\"...",
        f"Looking for matches...",
        f"Finding the best result...",
        f"Almost there..."
    ]
    
    i = 0
    while True:
        await asyncio.sleep(1.2)
        try:
            await msg.edit_text(f"{animations[i % len(animations)]} {texts[i % len(texts)]}")
            i += 1
        except:
            break

async def handle_music_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle music callback queries"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    _, action, music_id = data.split('_')
    
    if action == 'download':
        result = context.user_data.get('music_result')
        
        if not result or result.get('id') != music_id:
            await query.edit_message_text("❌ *Session Expired*\n\nPlease search again.", parse_mode='Markdown')
            return
        
        await query.edit_message_text("🎵 Downloading MP3...")
        
        try:
            file_path = await download_music(result['url'])
            
            if file_path:
                # Send audio
                await query.message.reply_audio(
                    audio=open(file_path, 'rb'),
                    title=result['title'],
                    performer=result['artist'],
                    duration=result.get('duration_seconds', 0)
                )
                
                # Clean up
                cleanup_file(file_path)
                await query.message.delete()
            else:
                await query.edit_message_text(
                    "❌ *MP3 Download Failed*\n\n"
                    "Could not download the audio file.\n"
                    "Please try again.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Music download error: {str(e)}", exc_info=True)
            await query.edit_message_text(
                f"❌ *Download Failed*\n\n{str(e)[:150]}",
                parse_mode='Markdown'
            )