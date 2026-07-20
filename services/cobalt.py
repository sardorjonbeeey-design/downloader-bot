"""
Cobalt API client - Shared for all services
"""
import aiohttp
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from config import config

logger = logging.getLogger(__name__)

class CobaltClient:
    """Shared Cobalt API client"""
    
    def __init__(self):
        self.api_url = f"{config.COBALT_API_URL}/api/json"
    
    async def download(self, url: str, options: Optional[Dict] = None) -> Optional[Path]:
        """Download content using Cobalt"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "url": url,
                    "videoQuality": "720",
                    "downloadMode": "auto",
                    **(options or {})
                }
                
                async with session.post(self.api_url, json=payload) as response:
                    if response.status != 200:
                        logger.error(f"Cobalt API error: {response.status}")
                        return None
                    
                    data = await response.json()
                    
                    if data.get('status') != 'ok':
                        logger.error(f"Cobalt error: {data.get('text')}")
                        return None
                    
                    download_url = data.get('url')
                    if not download_url:
                        return None
                    
                    filename = data.get('filename', 'download.mp4')
                    filepath = Path(config.DOWNLOAD_PATH) / filename
                    
                    async with session.get(download_url) as file_response:
                        if file_response.status == 200:
                            with open(filepath, 'wb') as f:
                                f.write(await file_response.read())
                            return filepath
                        return None
                            
        except Exception as e:
            logger.error(f"Cobalt download error: {str(e)}")
            return None

cobalt_client = CobaltClient()