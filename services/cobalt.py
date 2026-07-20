"""
Cobalt API - Proven working code from Qadam bot
All TikTok and Instagram downloads go through this ONE file
"""
import os
import re
import time
import logging
import asyncio
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

import aiohttp

from config import config

logger = logging.getLogger(__name__)

# Your Cobalt URL from .env
COBALT_API_URL = config.COBALT_API_URL

# Platforms where audio is preferred
AUDIO_ONLY_DOMAINS = ("soundcloud.com", "music.youtube.com")

# Error messages
ERROR_MESSAGES = {
    "error.api.link.invalid": "❌ Havola noto'g'ri.",
    "error.api.link.unsupported": "❌ Platforma qo'llab-quvvatlanmaydi.",
    "error.api.fetch.empty": "🔒 Post yopiq (private) yoki o'chirilgan.",
    "error.api.fetch.fail": "⚠️ Yuklab bo'lmadi. Qayta urinib ko'ring.",
    "error.api.fetch.critical": "⚠️ Texnik xatolik. Qayta urinib ko'ring.",
    "error.api.fetch.rate": "⏳ Juda ko'p so'rov. Birozdan keyin urinib ko'ring.",
    "error.api.rate_exceeded": "⏳ Juda ko'p so'rov. Birozdan keyin urinib ko'ring.",
    "error.api.content.too_long": "📏 Fayl juda uzun.",
    "error.api.youtube.login": "🔒 Video login talab qiladi.",
}
DEFAULT_ERROR_MESSAGE = "😕 Havolani qayta ishlab bo'lmadi."


class CobaltClient:
    """Cobalt API client - single source of truth"""
    
    def __init__(self):
        self.api_url = COBALT_API_URL
        logger.info(f"✅ Cobalt API: {self.api_url}")
    
    async def resolve_link(self, url: str) -> Tuple[Optional[dict], Optional[str]]:
        """Calls Cobalt to resolve a media URL"""
        if not self.api_url:
            logger.warning("COBALT_API_URL not set")
            return None, "not_configured"

        endpoint = self.api_url.rstrip("/") + "/"
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        download_mode = "audio" if any(d in url.lower() for d in AUDIO_ONLY_DOMAINS) else "auto"
        body = {"url": url, "videoQuality": "1080", "downloadMode": download_mode}

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(endpoint, headers=headers, json=body) as resp:
                    try:
                        data = await resp.json()
                    except (aiohttp.ContentTypeError, ValueError) as e:
                        logger.error(f"Cobalt non-JSON response: {e}")
                        return None, "invalid_response"

                    if resp.status >= 500:
                        logger.error(f"Cobalt server error {resp.status}: {data}")
                        return None, "offline"

                    logger.info(f"Cobalt resolved {url} -> status={data.get('status')}")
                    return data, None
        except asyncio.TimeoutError:
            logger.error(f"Cobalt timeout for {url}")
            return None, "timeout"
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Cannot reach Cobalt: {e}")
            return None, "offline"
        except aiohttp.ClientError as e:
            logger.error(f"Cobalt request failed: {e}")
            return None, "offline"

    def extract_link_and_note(self, data: dict) -> Tuple[Optional[str], str]:
        """Extract download link from Cobalt response"""
        status = data.get("status")

        if status in ("redirect", "tunnel"):
            return data.get("url"), ""

        if status == "picker":
            items = data.get("picker") or []
            if items:
                note = f" (jami {len(items)} ta fayl, birinchisi yuborildi)" if len(items) > 1 else ""
                return items[0].get("url"), note
            return None, ""

        return None, ""

    async def download(self, url: str) -> Optional[Path]:
        """Download media using Cobalt - returns file path"""
        data, reason = await self.resolve_link(url)
        
        if reason:
            logger.error(f"Cobalt error: {reason}")
            return None
        
        if not data:
            return None
        
        link, note = self.extract_link_and_note(data)
        
        if not link:
            code = (data.get("error") or {}).get("code")
            logger.error(f"Cobalt error code: {code}")
            return None
        
        # Download the file
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(link) as response:
                    if response.status == 200:
                        filename = data.get('filename', 'download.mp4')
                        filepath = Path(config.DOWNLOAD_PATH) / filename
                        
                        # Ensure directory exists
                        filepath.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(filepath, 'wb') as f:
                            f.write(await response.read())
                        
                        logger.info(f"✅ Downloaded: {filepath}")
                        return filepath
                    else:
                        logger.error(f"Failed to download file: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"File download error: {str(e)}")
            return None


# Create the cobalt instance that other files import
cobalt = CobaltClient()


# Legacy function for backward compatibility
async def download_with_cobalt(url: str) -> Optional[Path]:
    """Legacy function - uses cobalt.download()"""
    return await cobalt.download(url)