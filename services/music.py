"""
Music search - With streaming support
"""
import logging
import asyncio
import yt_dlp
from typing import List, Dict, Any, Optional, Tuple

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
            
            duration = int(entry.get('duration', 0))
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
        logger.error(f"Music search error: {str(e)}")
        return []

async def download_music(url: str) -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
    """Download music and return (file_data, filename, error)"""
    try:
        opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestaudio/best',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }
            ]
        }
        
        def sync_download():
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    return None
                filename = ydl.prepare_filename(info).replace('.mp4', '.mp3').replace('.webm', '.mp3')
                if Path(filename).exists():
                    return Path(filename)
                return None
        
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, sync_download)
        
        if not file_path or not file_path.exists():
            return None, None, "Download failed"
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        file_path.unlink()
        
        return file_data, file_path.name, None
        
    except Exception as e:
        return None, None, str(e)[:100]