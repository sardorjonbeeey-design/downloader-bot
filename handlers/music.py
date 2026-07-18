"""
Music search and download handlers
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.music import search_music, download_music
from utils.helpers import cleanup_file

logger = logging.getLogger(__name__)

async def handle_music_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle music search query"""
    query_text = update.message.text.strip()
    
    # Show searching message
    status_msg = await update.message.reply_text(
        f"🔍 Searching for \"{query_text}\"..."
    )
    
    try:
        results = await search_music(query_text)
        
        if not results:
            await status_msg.edit_text(
                f"❌ No results found for \"{query_text}\"\n"
                "Please try a different search term."
            )
            return
        
        # Show first result (best match)
        result = results[0]
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎵 Download MP3", callback_data=f"music_download_{result['id']}"),
                InlineKeyboardButton("▶️ Watch on YouTube", url=result['url'])
            ]
        ])
        
        await status_msg.delete()
        
        # Send music info
        await update.message.reply_photo(
            photo=result['thumbnail'],
            caption=(
                f"🎵 *{result['title']}*\n"
                f"👤 *Artist:* {result['artist']}\n"
                f"⏱️ *Duration:* {result['duration']}\n\n"
                f"Select an option below:"
            ),
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        # Store result for later use
        context.user_data['music_result'] = result
        
    except Exception as e:
        logger.error(f"Music search error: {str(e)}", exc_info=True)
        await status_msg.edit_text(
            f"❌ Search failed: {str(e)}\n"
            "Please try again."
        )

async def handle_music_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle music callback queries"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    _, action, music_id = data.split('_')
    
    if action == 'download':
        result = context.user_data.get('music_result')
        
        if not result or result.get('id') != music_id:
            await query.edit_message_text("❌ Session expired. Please search again.")
            return
        
        await query.edit_message_text("🔄 Downloading MP3...")
        
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
                
        except Exception as e:
            logger.error(f"Music download error: {str(e)}", exc_info=True)
            await query.edit_message_text(f"❌ Download failed: {str(e)}")