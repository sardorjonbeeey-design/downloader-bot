"""
Cobalt API - Complete client with streaming support
No file storage - streams directly to user
"""
import os
import logging
import asyncio
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

import aiohttp

from config import config

logger = logging.getLogger(__name__)

COBALT_API_URL = config.COBALT_API_URL

# Error messages
ERROR_MESSAGES = {
    "error.api.link.invalid": "❌ Invalid link",
    "error.api.link.unsupported": "❌ Platform not supported",
    "error.api.fetch.empty": "🔒 Content is private or deleted",
    "error.api.fetch.fail": "⚠️ Download failed. Try again.",
    "error.api.fetch.critical": "⚠️ Server error. Try again.",
    "error.api.fetch.rate": "⏳ Rate limit. Try again later.",
    "error.api.rate_exceeded": "⏳ Too many requests. Try again later.",
    "error.api.content.too_long": "📏 Content is too long.",
    "error.api.youtube.login": "🔒 YouTube login required.",
}
DEFAULT_ERROR_MESSAGE = "😕 Could not process link."


class CobaltClient:
    """Complete Cobalt client with streaming support"""
    
    def __init__(self):
        self.api_url = COBALT_API_URL.rstrip("/") + "/"
        logger.info(f"✅ Cobalt API: {self.api_url}")
    
    async def download(self, url: str) -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
        """
        Download media using Cobalt - STREAMS DIRECTLY
        Returns: (file_data, filename, error_message)
        No file storage - streams directly to user
        """
        if not self.api_url:
            logger.warning("COBALT_API_URL not set")
            return None, None, "Cobalt not configured"
        
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        body = {"url": url, "videoQuality": "1080", "downloadMode": "auto"}
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                async with session.post(self.api_url, headers=headers, json=body) as resp:
                    if resp.status >= 500:
                        return None, None, "Cobalt server error"
                    
                    try:
                        data = await resp.json()
                    except:
                        return None, None, "Invalid response"
                    
                    # Check for Cobalt errors
                    if data.get('status') == 'error':
                        error_code = (data.get('error') or {}).get('code')
                        error_msg = ERROR_MESSAGES.get(error_code, DEFAULT_ERROR_MESSAGE)
                        return None, None, error_msg
                    
                    # Extract download URL
                    download_url = None
                    filename = 'download.mp4'
                    
                    if data.get('status') in ('redirect', 'tunnel'):
                        download_url = data.get('url')
                    elif data.get('status') == 'picker':
                        items = data.get('picker') or []
                        if items:
                            download_url = items[0].get('url')
                            if len(items) > 1:
                                logger.info(f"Multiple files: {len(items)} available")
                    
                    if not download_url:
                        return None, None, "No download link found"
                    
                    filename = data.get('filename', 'download.mp4')
                    
                    # STREAM THE FILE - NO STORAGE
                    async with session.get(download_url) as file_resp:
                        if file_resp.status != 200:
                            return None, None, "Failed to download file"
                        
                        # Read file content directly into memory
                        # For files > 50MB, Telegram will reject anyway
                        file_data = await file_resp.read()
                        
                        # Check size limit before returning
                        file_size_mb = len(file_data) / (1024 * 1024)
                        if file_size_mb > config.MAX_FILE_SIZE:
                            return None, None, f"File too large: {file_size_mb:.1f}MB (max {config.MAX_FILE_SIZE}MB)"
                        
                        logger.info(f"✅ Downloaded: {filename} ({file_size_mb:.1f}MB)")
                        return file_data, filename, None
                            
        except asyncio.TimeoutError:
            return None, None, "Request timed out"
        except aiohttp.ClientConnectorError:
            return None, None, "Cannot reach Cobalt"
        except Exception as e:
            logger.error(f"Cobalt error: {str(e)}")
            return None, None, str(e)[:100]


# Create instance
cobalt = CobaltClient()


async def download_with_cobalt(url: str) -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
    """Legacy function - returns (file_data, filename, error)"""
    return await cobalt.download(url)