"""
URL and input validators
"""
import re
from typing import Optional
from urllib.parse import urlparse

from config import config

def detect_url_type(text: str) -> Optional[str]:
    """
    Detect the type of URL or input
    
    Args:
        text: Input text to analyze
        
    Returns:
        Platform name or 'music' if not a URL
    """
    text = text.strip()
    
    # Check if it's a URL
    try:
        parsed = urlparse(text)
        if not parsed.scheme:
            # Try adding https://
            parsed = urlparse(f"https://{text}")
            if not parsed.netloc:
                return 'music'
    except:
        return 'music'
    
    domain = parsed.netloc.lower()
    
    # Check against supported platforms
    for platform, domains in config.SUPPORTED_PLATFORMS.items():
        for supported_domain in domains:
            if supported_domain in domain:
                return platform
    
    # If it's a URL but not supported, treat as music search
    if parsed.scheme and parsed.netloc:
        # Check if it might be a music video link
        if 'youtube.com' in domain or 'youtu.be' in domain:
            return 'youtube'
        return 'music'
    
    return 'music'

def is_music_search(text: str) -> bool:
    """
    Determine if text is a music search query
    
    Args:
        text: Input text
        
    Returns:
        True if it's likely a music search
    """
    text = text.strip()
    
    # If it's a URL, it's not a music search
    if re.match(r'^https?://', text):
        return False
    
    # Check if it looks like a music search
    # More than 3 words or contains common music terms
    words = text.split()
    if len(words) > 3:
        return True
    
    # Check for common music indicators
    music_indicators = ['song', 'music', 'artist', 'cover', 'remix', 'live']
    if any(indicator in text.lower() for indicator in music_indicators):
        return True
    
    # Check for artist - song pattern
    if ' - ' in text or ' by ' in text.lower():
        return True
    
    return False

def validate_url(url: str) -> bool:
    """Validate if string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_instagram_post_id(url: str) -> Optional[str]:
    """Extract Instagram post ID from URL"""
    patterns = [
        r'instagram\.com/p/([A-Za-z0-9_-]+)',
        r'instagram\.com/reel/([A-Za-z0-9_-]+)',
        r'instagram\.com/tv/([A-Za-z0-9_-]+)',
        r'instagram\.com/stories/([A-Za-z0-9_-]+)/(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def extract_youtube_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL"""
    patterns = [
        r'youtu\.be/([A-Za-z0-9_-]{11})',
        r'youtube\.com/watch\?v=([A-Za-z0-9_-]{11})',
        r'youtube\.com/embed/([A-Za-z0-9_-]{11})',
        r'youtube\.com/v/([A-Za-z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def extract_tiktok_video_id(url: str) -> Optional[str]:
    """Extract TikTok video ID from URL"""
    patterns = [
        r'tiktok\.com/@([^/]+)/video/(\d+)',
        r'tiktok\.com/([^?]+)\?',
        r'vm\.tiktok\.com/([A-Za-z0-9]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1) if len(match.groups()) == 1 else match.group(2)
    return None