"""
Handlers - Export all handlers from their respective files
"""
from handlers.start import start_command, help_command, info_command
from handlers.download import handle_url
from handlers.youtube import handle_youtube, youtube_callback_handler
from handlers.music import handle_music_search, handle_music_callback
from handlers.admin import stats_command, reset_stats

__all__ = [
    'start_command',
    'help_command',
    'info_command',
    'handle_url',
    'handle_youtube',
    'youtube_callback_handler',
    'handle_music_search',
    'handle_music_callback',
    'stats_command',
    'reset_stats',
]