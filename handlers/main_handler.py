async def handle_music_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle music search - with better error handling"""
    query = update.message.text.strip()
    
    # Send initial message
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
            except Exception as e:
                # If edit fails, send new message
                await update.message.reply_text(
                    f"❌ Natija topilmadi\n\n"
                    f"\"{query}\"\n\n"
                    "Urinib ko'ring:\n"
                    "• Boshqa imlo\n"
                    "• Artist + qo'shiq nomi"
                )
            return
        
        result = results[0]
        
        # Delete status message safely
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
        
        await update.message.reply_photo(
            photo=result['thumbnail'],
            caption=(
                f"🎵 *{result['title']}*\n"
                f"👤 Artist · {result['artist']}\n"
                f"⏱️ Davomiyligi · {result['duration']}\n\n"
                f"📥 Tanlang:"
            ),
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