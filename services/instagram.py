"""
Instagram downloader service
"""
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from services.downloader import DownloaderService
from utils.helpers import cleanup_file

logger = logging.getLogger(__name__)

class InstagramService(DownloaderService):
    """Instagram content downloader"""
    
    async def download_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Download Instagram content
        
        Args:
            url: Instagram URL
            
        Returns:
            Dictionary with file info and metadata
        """
        try:
            opts = self.get_ydl_opts('best')
            opts.update({
                'cookiesfrombrowser': ('chrome',),
                'extract_flat': False,
            })
            
            # Check if it's a story
            if 'stories' in url:
                opts['latest'] = True
                opts['max_downloads'] = 1
            
            file_path = await self.download(url, opts)
            
            if not file_path or not file_path.exists():
                return None
            
            # Determine content type
            content_type = 'photo'
            if file_path.suffix in ['.mp4', '.mov']:
                content_type = 'video'
                
            return {
                'file_path': str(file_path),
                'type': content_type,
                'caption': '📸 Instagram content downloaded successfully!',
                'source': 'instagram'
            }
            
        except Exception as e:
            logger.error(f"Instagram download error: {str(e)}", exc_info=True)
            return None

# Singleton instance
instagram_service = InstagramService()

async def download_instagram(url: str) -> Optional[Dict[str, Any]]:
    """Download Instagram content"""
    return await instagram_service.download_content(url)