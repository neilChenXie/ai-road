"""
Platform detection for video URLs
"""

import re
from urllib.parse import urlparse
from typing import Dict, Optional, Tuple


class PlatformDetector:
    """Detect video platform from URL"""

    PATTERNS = {
        'youtube': [
            r'youtube\.com/watch',
            r'youtu\.be/',
            r'youtube\.com/shorts/',
        ],
        'bilibili': [
            r'bilibili\.com/video/',
            r'b23\.tv/',
        ],
        'xiaohongshu': [
            r'xiaohongshu\.com',
            r'xhslink\.com',
        ],
        'tiktok': [
            r'tiktok\.com/@',
            r'vm\.tiktok\.com',
        ],
        'twitter': [
            r'twitter\.com/',
            r'x\.com/',
        ],
        'instagram': [
            r'instagram\.com/reel',
            r'instagram\.com/p/',
        ],
        'vimeo': [
            r'vimeo\.com/',
        ],
        'twitch': [
            r'twitch\.tv/videos/',
        ],
        'douyin': [
            r'douyin\.com/',
        ],
    }

    PLATFORM_CONFIG = {
        'youtube': {
            'name': 'YouTube',
            'supports_api': False,
            'supports_cookies': True,
            'preferred_cookies': 'chrome',
            'max_quality': 1080,
        },
        'bilibili': {
            'name': 'Bilibili (B站)',
            'supports_api': True,
            'supports_cookies': False,
            'bypass_412': True,
        },
        'xiaohongshu': {
            'name': 'XiaoHongShu (小红书)',
            'supports_api': False,
            'supports_cookies': True,
            'preferred_cookies': 'chrome',
            'requires_auth': True,
        },
        'tiktok': {
            'name': 'TikTok',
            'supports_api': False,
            'supports_cookies': True,
        },
        'twitter': {
            'name': 'Twitter/X',
            'supports_api': False,
            'supports_cookies': True,
        },
        'instagram': {
            'name': 'Instagram',
            'supports_api': False,
            'supports_cookies': True,
        },
        'vimeo': {
            'name': 'Vimeo',
            'supports_api': False,
            'supports_cookies': False,
        },
        'twitch': {
            'name': 'Twitch',
            'supports_api': False,
            'supports_cookies': True,
        },
        'douyin': {
            'name': '抖音',
            'supports_api': False,
            'supports_cookies': True,
        },
    }

    def __init__(self):
        pass

    def detect(self, url: str) -> Tuple[Optional[str], Dict]:
        """
        Detect platform from URL

        Args:
            url: Video URL

        Returns:
            Tuple of (platform_key, platform_config)
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        # Check each platform pattern
        for platform, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, domain + path):
                    return platform, self.PLATFORM_CONFIG.get(platform, {})

        # Unknown platform - return None
        return None, {
            'name': 'Unknown',
            'supports_api': False,
            'supports_cookies': True,
        }

    def get_video_id(self, url: str, platform: str) -> Optional[str]:
        """
        Extract video ID from URL

        Args:
            url: Video URL
            platform: Platform key

        Returns:
            Video ID or None
        """
        parsed = urlparse(url)

        if platform == 'youtube':
            # youtube.com/watch?v=VIDEO_ID
            if 'watch' in parsed.path:
                params = dict(p.split('=') for p in parsed.query.split('&') if '=' in p)
                return params.get('v')
            # youtu.be/VIDEO_ID
            if 'youtu.be' in parsed.netloc:
                return parsed.path.strip('/')
            # youtube.com/shorts/VIDEO_ID
            if 'shorts' in parsed.path:
                return parsed.path.split('/')[-1]

        elif platform == 'bilibili':
            # Extract BV ID
            if 'b23.tv' in parsed.netloc:
                return parsed.path.strip('/')
            if 'video' in parsed.path:
                return parsed.path.split('/')[-1]

        elif platform == 'xiaohongshu':
            # Extract ID from path
            if 'discovery/item' in parsed.path:
                parts = parsed.path.split('/')
                for part in parts:
                    if part.isdigit() or re.match(r'^[0-9a-f]{24}$', part):
                        return part

        elif platform in ['tiktok', 'instagram', 'vimeo', 'twitch']:
            return parsed.path.split('/')[-1]

        # For unknown platforms, just use a hash of the URL
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:16]

    def is_supported(self, url: str) -> bool:
        """Check if platform is supported"""
        platform, _ = self.detect(url)
        return platform is not None

    def get_supported_platforms(self) -> Dict[str, str]:
        """Get list of supported platforms"""
        return {k: v['name'] for k, v in self.PLATFORM_CONFIG.items()}

    def needs_cookies(self, url: str, config: Dict) -> bool:
        """Check if platform needs cookies"""
        platform, platform_config = self.detect(url)

        # Override with provided config
        if config.get('use_cookies') is False:
            return False

        return platform_config.get('supports_cookies', False)

    def get_preferred_browser(self, url: str, config: Dict) -> str:
        """Get preferred browser for cookies"""
        platform, platform_config = self.detect(url)
        return config.get('cookies_browser',
                          platform_config.get('preferred_cookies', 'chrome'))


if __name__ == '__main__':
    detector = PlatformDetector()

    # Test URLs
    test_urls = [
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'https://b23.tv/abc123',
        'https://www.xiaohongshu.com/discovery/item/123456',
        'https://tiktok.com/@user/video/123',
    ]

    for url in test_urls:
        platform, config = detector.detect(url)
        video_id = detector.get_video_id(url, platform)
        print(f"URL: {url}")
        print(f"  Platform: {platform} - {config.get('name', 'Unknown')}")
        print(f"  Video ID: {video_id}")
        print()
