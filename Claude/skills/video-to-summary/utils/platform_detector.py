#!/usr/bin/env python3
"""
平台检测模块 - 检测视频URL所属平台
"""

import re
import logging
from typing import Dict, Optional, Tuple, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# 平台正则表达式模式
PLATFORM_PATTERNS = {
    "youtube": [
        r"youtube\.com/watch\?v=",
        r"youtu\.be/",
        r"youtube\.com/shorts/",
        r"youtube\.com/embed/",
        r"youtube\.com/v/"
    ],
    "youtube_music": [
        r"music\.youtube\.com"
    ],
    "bilibili": [
        r"bilibili\.com/video/",
        r"b23\.tv/",
        r"bilibili\.tv/"
    ],
    "xiaohongshu": [
        r"xiaohongshu\.com/discovery/",
        r"xhslink\.com/",
        r"xiaohongshu\.com/explore/"
    ],
    "douyin": [
        r"douyin\.com/video/",
        r"iesdouyin\.com/share/video/",
        r"douyin\.com/share/video/"
    ],
    "tiktok": [
        r"tiktok\.com/@",
        r"tiktok\.com/v/",
        r"vm\.tiktok\.com/",
        r"vt\.tiktok\.com/"
    ],
    "twitter": [
        r"twitter\.com/",
        r"x\.com/",
        r"t\.co/"
    ],
    "instagram": [
        r"instagram\.com/(p|reel|tv)/",
        r"instagr\.am/"
    ],
    "facebook": [
        r"facebook\.com/watch/",
        r"fb\.watch/"
    ],
    "vimeo": [
        r"vimeo\.com/"
    ],
    "twitch": [
        r"twitch\.tv/videos/",
        r"twitch\.tv/clips/"
    ],
    "netease_music": [
        r"music\.163\.com/#/video\?id=",
        r"music\.163\.com/video/"
    ],
    "iqiyi": [
        r"iqiyi\.com/v_",
        r"iq\.com/"
    ],
    "youku": [
        r"youku\.com/v_show/",
        r"v\.youku\.com/v_show/"
    ],
    "tencent_video": [
        r"v\.qq\.com/x/",
        r"v\.qq\.com/txp/iframe/"
    ],
    "migu": [
        r"miguvideo\.com/"
    ]
}

# 平台友好名称
PLATFORM_NAMES = {
    "youtube": "YouTube",
    "youtube_music": "YouTube Music",
    "bilibili": "Bilibili (B站)",
    "xiaohongshu": "小红书",
    "douyin": "抖音",
    "tiktok": "TikTok",
    "twitter": "Twitter/X",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "vimeo": "Vimeo",
    "twitch": "Twitch",
    "netease_music": "网易云音乐",
    "iqiyi": "爱奇艺",
    "youku": "优酷",
    "tencent_video": "腾讯视频",
    "migu": "咪咕视频",
    "generic": "通用视频"
}

# 平台特定配置
PLATFORM_CONFIGS = {
    "youtube": {
        "needs_cookies": True,
        "recommended_browser": "chrome",
        "quality_options": ["best", "1080p", "720p", "480p", "audio"],
        "supports_subtitles": True,
        "supports_playlist": True
    },
    "bilibili": {
        "needs_cookies": False,
        "needs_referer": True,
        "quality_options": ["best", "1080p", "720p", "480p"],
        "supports_subtitles": True,
        "supports_playlist": True
    },
    "xiaohongshu": {
        "needs_cookies": False,
        "needs_user_agent": True,
        "quality_options": ["best"],
        "supports_subtitles": False,
        "supports_playlist": False
    },
    "douyin": {
        "needs_cookies": False,
        "needs_user_agent": True,
        "quality_options": ["best"],
        "supports_subtitles": False,
        "supports_playlist": False
    },
    "generic": {
        "needs_cookies": False,
        "quality_options": ["best", "audio"],
        "supports_subtitles": False,
        "supports_playlist": False
    }
}

def detect_platform(url: str) -> str:
    """
    检测URL所属平台
    
    Args:
        url: 视频URL
    
    Returns:
        平台标识符
    """
    try:
        # 规范化URL
        normalized_url = url.lower().strip()
        
        # 检查每个平台的正则表达式
        for platform_id, patterns in PLATFORM_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, normalized_url):
                    logger.info(f"检测到平台: {platform_id} ({PLATFORM_NAMES.get(platform_id, platform_id)})")
                    return platform_id
        
        # 如果没有匹配，尝试从域名推断
        parsed_url = urlparse(normalized_url)
        domain = parsed_url.netloc
        
        # 常见的视频域名关键词
        video_keywords = ["video", "watch", "play", "stream", "tube", "tv"]
        for keyword in video_keywords:
            if keyword in domain:
                logger.info(f"根据域名关键词 '{keyword}' 推断为通用视频")
                return "generic"
        
        logger.info("未识别到具体平台，使用通用处理")
        return "generic"
        
    except Exception as e:
        logger.error(f"平台检测失败: {e}")
        return "generic"

def get_platform_info(url: str) -> Dict:
    """
    获取平台详细信息
    
    Args:
        url: 视频URL
    
    Returns:
        平台信息字典
    """
    platform_id = detect_platform(url)
    platform_name = PLATFORM_NAMES.get(platform_id, platform_id)
    config = PLATFORM_CONFIGS.get(platform_id, PLATFORM_CONFIGS["generic"])
    
    return {
        "id": platform_id,
        "name": platform_name,
        "config": config,
        "url": url
    }

def is_supported_platform(url: str) -> bool:
    """
    检查平台是否支持
    
    Args:
        url: 视频URL
    
    Returns:
        是否支持
    """
    platform_id = detect_platform(url)
    
    # 检查是否在已知平台列表中
    if platform_id in PLATFORM_PATTERNS:
        return True
    
    # 检查是否为通用视频
    if platform_id == "generic":
        return True
    
    return False

def get_platform_recommendations(url: str) -> Dict:
    """
    获取平台特定建议
    
    Args:
        url: 视频URL
    
    Returns:
        建议字典
    """
    platform_info = get_platform_info(url)
    platform_id = platform_info["id"]
    config = platform_info["config"]
    
    recommendations = {
        "platform": platform_info["name"],
        "general": [],
        "yt-dlp_options": [],
        "api_support": {}
    }
    
    # 通用建议
    if config.get("needs_cookies", False):
        recommendations["general"].append("此平台需要浏览器cookies以避免403错误")
        recommendations["yt-dlp_options"].append("--cookies-from-browser chrome")
    
    if config.get("needs_referer", False):
        recommendations["general"].append("此平台需要设置referer")
        recommendations["yt-dlp_options"].append("--referer '平台URL'")
    
    if config.get("needs_user_agent", False):
        recommendations["general"].append("此平台需要自定义user-agent")
        recommendations["yt-dlp_options"].append("--user-agent 'Mozilla/5.0'")
    
    # B站特定建议（412问题解决方案）
    if platform_id == "bilibili":
        recommendations["general"].append("⚠️  B站有412反爬机制，建议使用API方案")
        recommendations["general"].append("✅  已实现B站API支持，可绕过412问题")
        
        # API支持信息
        recommendations["api_support"] = {
            "available": True,
            "name": "Bilibili API",
            "features": [
                "绕过412反爬机制",
                "获取完整视频信息",
                "获取多质量下载地址",
                "支持短链接(b23.tv)",
                "获取字幕信息"
            ],
            "recommended": True
        }
    
    # YouTube API支持
    elif platform_id == "youtube":
        recommendations["api_support"] = {
            "available": True,
            "name": "YouTube Data API",
            "features": ["获取视频信息", "搜索视频", "获取频道信息"],
            "requires_key": True
        }
    
    # 质量选项建议
    if "quality_options" in config:
        recommendations["quality_options"] = config["quality_options"]
    
    # 功能支持
    support_info = []
    if config.get("supports_subtitles", False):
        support_info.append("字幕下载")
    if config.get("supports_playlist", False):
        support_info.append("播放列表支持")
    
    if support_info:
        recommendations["supported_features"] = support_info
    
    return recommendations

def extract_video_id(url: str, platform: str = None) -> Optional[str]:
    """
    从URL提取视频ID
    
    Args:
        url: 视频URL
        platform: 平台标识符（可选）
    
    Returns:
        视频ID，无法提取返回None
    """
    try:
        if not platform:
            platform = detect_platform(url)
        
        url = url.strip()
        
        # 平台特定的ID提取逻辑
        if platform == "youtube":
            # YouTube: https://www.youtube.com/watch?v=VIDEO_ID
            match = re.search(r"(?:v=|youtu\.be/|embed/|v/)([a-zA-Z0-9_-]{11})", url)
            return match.group(1) if match else None
        
        elif platform == "bilibili":
            # Bilibili: https://www.bilibili.com/video/BV1xx411c7mD
            match = re.search(r"/video/(BV[a-zA-Z0-9]+)", url)
            return match.group(1) if match else None
        
        elif platform == "xiaohongshu":
            # 小红书: https://www.xiaohongshu.com/discovery/item/64b7e8b4000000001e03b6e4
            match = re.search(r"/discovery/item/([a-f0-9]+)", url)
            return match.group(1) if match else None
        
        elif platform == "douyin":
            # 抖音: https://www.douyin.com/video/7231234567890123456
            match = re.search(r"/video/(\d+)", url)
            return match.group(1) if match else None
        
        elif platform == "twitter":
            # Twitter/X: https://twitter.com/user/status/1234567890123456789
            match = re.search(r"/status/(\d+)", url)
            return match.group(1) if match else None
        
        else:
            # 通用提取：尝试从URL路径中提取最后一段
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            if path_parts:
                return path_parts[-1]
            
            return None
            
    except Exception as e:
        logger.error(f"提取视频ID失败: {e}")
        return None

def validate_url(url: str) -> Tuple[bool, str]:
    """
    验证URL是否有效
    
    Args:
        url: 待验证的URL
    
    Returns:
        (是否有效, 错误消息)
    """
    try:
        # 基本URL格式检查
        if not url or not url.strip():
            return False, "URL不能为空"
        
        # 检查是否包含协议
        if not url.startswith(('http://', 'https://')):
            return False, "URL必须以http://或https://开头"
        
        # 解析URL
        parsed = urlparse(url)
        
        # 检查是否有网络位置
        if not parsed.netloc:
            return False, "URL缺少域名或主机名"
        
        # 检查是否支持该平台
        if not is_supported_platform(url):
            logger.warning(f"URL可能来自不受支持的平台: {url}")
            # 这里不返回失败，因为yt-dlp可能支持更多平台
        
        return True, "URL格式正确"
        
    except Exception as e:
        return False, f"URL验证失败: {e}"

def get_platform_icon(platform_id: str) -> str:
    """
    获取平台图标（Emoji）
    
    Args:
        platform_id: 平台标识符
    
    Returns:
        平台图标Emoji
    """
    icons = {
        "youtube": "📺",
        "youtube_music": "🎵",
        "bilibili": "🇧",
        "xiaohongshu": "📕",
        "douyin": "🎵",
        "tiktok": "💃",
        "twitter": "🐦",
        "instagram": "📷",
        "facebook": "📘",
        "vimeo": "🎬",
        "twitch": "🟣",
        "netease_music": "☁️",
        "iqiyi": "🍿",
        "youku": "📺",
        "tencent_video": "🐧",
        "migu": "📱",
        "generic": "🎥"
    }
    
    return icons.get(platform_id, "📁")

def has_api_support(url: str) -> Dict[str, Any]:
    """
    检查平台是否有API支持
    
    Args:
        url: 视频URL
    
    Returns:
        API支持信息字典
    """
    try:
        platform_id = detect_platform(url)
        
        api_info = {
            "platform": platform_id,
            "has_api": False,
            "api_name": None,
            "features": [],
            "recommended": False,
            "requires_auth": False
        }
        
        # B站API支持
        if platform_id == "bilibili":
            # 尝试导入B站API模块来验证可用性
            try:
                from .bilibili_api import can_use_bilibili_api, extract_bvid_from_url
                
                if can_use_bilibili_api(url):
                    bvid = extract_bvid_from_url(url)
                    api_info.update({
                        "has_api": True,
                        "api_name": "Bilibili API",
                        "features": [
                            "绕过412反爬机制",
                            "获取视频信息和元数据",
                            "获取下载地址",
                            "支持短链接",
                            "获取字幕信息"
                        ],
                        "recommended": True,
                        "requires_auth": False,
                        "bvid": bvid,
                        "status": "可用"
                    })
                else:
                    api_info["status"] = "URL格式不支持"
            except ImportError:
                api_info["status"] = "API模块未安装"
            except Exception as e:
                api_info["status"] = f"检测失败: {str(e)}"
        
        # YouTube API支持（需要API key）
        elif platform_id == "youtube":
            api_info.update({
                "has_api": True,
                "api_name": "YouTube Data API",
                "features": ["获取视频信息", "搜索功能", "获取频道信息"],
                "recommended": False,  # 需要API key，不推荐默认使用
                "requires_auth": True,
                "status": "需要API key"
            })
        
        return api_info
        
    except Exception as e:
        logger.error(f"检查API支持失败: {e}")
        return {
            "platform": "unknown",
            "has_api": False,
            "status": f"检查失败: {str(e)}"
        }

if __name__ == '__main__':
    # 测试代码
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.bilibili.com/video/BV1GJ411x7h7",
        "https://www.xiaohongshu.com/discovery/item/64b7e8b4000000001e03b6e4",
        "https://vimeo.com/123456789",
        "https://example.com/video/123"
    ]
    
    for url in test_urls:
        platform = detect_platform(url)
        info = get_platform_info(url)
        video_id = extract_video_id(url, platform)
        
        print(f"\nURL: {url}")
        print(f"平台: {platform} ({info['name']})")
        print(f"视频ID: {video_id}")
        
        if platform != "generic":
            rec = get_platform_recommendations(url)
            print(f"建议: {rec['general']}")