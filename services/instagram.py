"""
Instagram downloader service - Fixed
"""
import logging
import yt_dlp
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

from services.downloader import DownloaderService

logger = logging.getLogger(__name__)

class InstagramService(DownloaderService):
    """Instagram content downloader - Fixed for public content"""
    
    async def download_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Download Instagram content"""
        try:
            # Clean URL - remove tracking parameters
            if '?' in url:
                url = url.split('?')[0]
            
            opts = self.get_ydl_opts('best')
            opts.update({
                'extract_flat': False,
                'ignoreerrors': True,
                'no_warnings': True,
                'quiet': True,
                # Instagram specific
                'username': 'YOUR_INSTAGRAM_USERNAME',  # Optional
                'password': 'YOUR_INSTAGRAM_PASSWORD',  # Optional
            })
            
            # Try without cookies first
            try:
                file_path = await self.download(url, opts)
            except Exception as e:
                logger.warning(f"First attempt failed: {e}")
                # Try with cookies if available
                if Path('cookies.txt').exists():
                    opts['cookiefile'] = 'cookies.txt'
                    file_path = await self.download(url, opts)
                else:
                    raise
            
            if not file_path or not file_path.exists():
                # Try alternative format
                opts2 = self.get_ydl_opts('bestvideo+bestaudio/best')
                opts2.update({
                    'extract_flat': False,
                    'ignoreerrors': True,
                    'no_warnings': True,
                    'quiet': True,
                })
                file_path = await self.download(url, opts2)
            
            if not file_path or not file_path.exists():
                logger.error(f"No file downloaded from {url}")
                return None
            
            # Determine content type
            content_type = 'photo'
            if file_path.suffix in ['.mp4', '.mov', '.webm']:
                content_type = 'video'
                
            return {
                'file_path': str(file_path),
                'type': content_type,
                'caption': 'Instagram content',
                'source': 'instagram'
            }
            
        except Exception as e:
            error_msg = str(e)
            if "login" in error_msg.lower() or "private" in error_msg.lower():
                logger.error(f"Instagram requires login: {error_msg}")
            else:
                logger.error(f"Instagram download error: {error_msg}", exc_info=True)
            return None

instagram_service = InstagramService()

async def download_instagram(url: str) -> Optional[Dict[str, Any]]:
    """Download Instagram content"""
    return await instagram_service.download_content(url)