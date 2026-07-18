"""
Inline keyboard definitions
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, List
from utils.helpers import format_file_size

def get_quality_keyboard(qualities: Dict[str, Dict], video_id: str) -> InlineKeyboardMarkup:
    """
    Create quality selection keyboard for YouTube videos
    
    Args:
        qualities: Dictionary of quality options
        video_id: YouTube video ID
        
    Returns:
        InlineKeyboardMarkup
    """
    keyboard = []
    
    for quality_key, quality_data in qualities.items():
        label = quality_data['label']
        size = quality_data.get('size')
        
        if size:
            button_text = f"{label} ({size})"
        else:
            button_text = label
            
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"quality_{quality_key}_{video_id}"
            )
        ])
    
    # Add audio option
    keyboard.append([
        InlineKeyboardButton(
            "🎵 Audio (MP3)",
            callback_data=f"quality_audio_{video_id}"
        )
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_music_keyboard(music_id: str) -> InlineKeyboardMarkup:
    """Create music action keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🎵 Download MP3", callback_data=f"music_download_{music_id}"),
            InlineKeyboardButton("▶️ YouTube", callback_data=f"music_open_{music_id}"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)