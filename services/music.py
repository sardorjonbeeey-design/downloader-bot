"""
Music search and download service
"""
import logging
import asyncio
import yt_dlp
from typing import List, Dict, Any, Optional
from pathlib import Path

from services.youtube import youtube_service
from utils.helpers import ensure_directory

logger = logging.getLogger(__name__)

async def search_music(query: str, limit: int = 1) -> List[Dict[str, Any]]:
    """Search for music on YouTube"""
    try:
        opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'default_search': 'ytsearch',
            'max_downloads': limit,
            'cookiesfrombrowser': ('chrome',),  # Add this
        }
        
        def sync_search():
            with yt_dlp.YoutubeDL(opts) as ydl:
                search_query = f"ytsearch{limit}:{query}"
                info = ydl.extract_info(search_query, download=False)
                return info.get('entries', [])
        
        loop = asyncio.get_event_loop()
        entries = await loop.run_in_executor(None, sync_search)
        
        results = []
        for entry in entries:
            if not entry:
                continue
                
            duration = entry.get('duration', 0)
            duration_str = f"{duration // 60}:{duration % 60:02d}"
            
            results.append({
                'id': entry.get('id'),
                'title': entry.get('title'),
                'artist': entry.get('uploader', 'Unknown'),
                'url': entry.get('webpage_url'),
                'thumbnail': entry.get('thumbnail'),
                'duration': duration_str,
                'duration_seconds': duration,
            })
            
        return results
        
    except Exception as e:
        logger.error(f"Music search error: {str(e)}", exc_info=True)
        return []

async def download_music(url: str) -> Optional[Path]:
    """Download music as MP3 from YouTube"""
    try:
        result = await youtube_service.download_audio(url)
        if result:
            return Path(result['file_path'])
        return None
        
    except Exception as e:
        logger.error(f"Music download error: {str(e)}", exc_info=True)
        return None