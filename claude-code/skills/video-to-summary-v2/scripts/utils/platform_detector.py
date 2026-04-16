"""
Platform Detector - Detect video platform from URL
"""

import re
from typing import Tuple, Dict, Optional
from urllib.parse import urlparse, parse_qs


class PlatformDetector:
    """Detect video platform and extract video ID"""

    # Platform patterns
    PATTERNS = {
        'bilibili': [
            r'(?:www\.)?bilibili\.com/video/(BV[a-zA-Z0-9]+)',
            r'(?:www\.)?bilibili\.com/video/av(\d+)',
            r'b23\.tv/(?:BV)?([a-zA-Z0-9]+)',
        ],
        'xiaohongshu': [
            r'(?:www\.)?xiaohongshu\.com/discovery/item/([a-zA-Z0-9]+)',
            r'(?:www\.)?xiaohongshu\.com/explore/([a-zA-Z0-9]+)',
            r'xhslink\.com/([a-zA-Z0-9]+)',
            r'(?:www\.)?xiaohongshu\.com/user/profile/[^/]+/([a-zA-Z0-9]+)',
        ]
    }

    # Platform configs
    PLATFORM_CONFIG = {
        'bilibili': {
            'name': 'B站',
            'name_en': 'Bilibili',
            'requires_cookies': False,
            'supports_short_link': True,
        },
        'xiaohongshu': {
            'name': '小红书',
            'name_en': 'XiaoHongShu',
            'requires_cookies': False,
            'supports_short_link': True,
            'requires_headers': True,
        }
    }

    def detect(self, url: str) -> Tuple[str, Dict]:
        """
        Detect platform from URL

        Args:
            url: Video URL

        Returns:
            Tuple of (platform_key, platform_config)
        """
        for platform, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return platform, self.PLATFORM_CONFIG.get(platform, {})

        return 'unknown', {'name': 'Unknown', 'name_en': 'Unknown'}

    def get_video_id(self, url: str, platform: str) -> Optional[str]:
        """
        Extract video ID from URL

        Args:
            url: Video URL
            platform: Detected platform

        Returns:
            Video ID or None
        """
        patterns = self.PATTERNS.get(platform, [])

        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def normalize_url(self, url: str, platform: str) -> str:
        """
        Normalize URL for processing

        Args:
            url: Original URL
            platform: Detected platform

        Returns:
            Normalized URL
        """
        # Handle short links - they need to be resolved first
        # yt-dlp handles this automatically
        return url

    def is_supported(self, url: str) -> bool:
        """Check if URL is from a supported platform"""
        platform, _ = self.detect(url)
        return platform != 'unknown'
