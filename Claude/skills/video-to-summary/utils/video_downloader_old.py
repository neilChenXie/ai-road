#!/usr/bin/env python3
"""
视频下载模块 - 支持多平台视频下载
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def download_video(
    url: str,
    output_dir: Path,
    platform: str = "generic",
    cookies_browser: str = "chrome",
    quality: str = "best"
) -> Optional[Path]:
    """
    下载视频
    
    Args:
        url: 视频URL
        output_dir: 输出目录
        platform: 平台类型
        cookies_browser: 浏览器cookies来源
        quality: 视频质量
    
    Returns:
        下载的视频文件路径，失败返回None
    """
    try:
        logger.info(f"开始下载视频: {url}")
        logger.info(f"平台: {platform}, 质量: {quality}")
        
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 构建yt-dlp命令
        cmd = ["yt-dlp", "-P", str(output_dir), "-o", "%(title)s.%(ext)s"]
        
        # 平台特定配置
        if platform in ["youtube", "youtube_music"]:
            # YouTube需要cookies避免403错误
            cmd.extend(["--cookies-from-browser", cookies_browser])
            logger.info(f"使用 {cookies_browser} 浏览器cookies")
        
        elif platform == "bilibili":
            # Bilibili可能需要referer
            cmd.extend(["--referer", "https://www.bilibili.com"])
            logger.info("设置Bilibili referer")
        
        elif platform == "xiaohongshu":
            # 小红书可能需要自定义user-agent
            cmd.extend(["--user-agent", "Mozilla/5.0"])
            logger.info("设置小红书user-agent")
        
        # 质量选择
        if quality == "720p":
            cmd.extend(["-f", "bestvideo[height<=720]+bestaudio/best[height<=720]"])
        elif quality == "1080p":
            cmd.extend(["-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]"])
        elif quality == "audio":
            # 仅下载音频
            cmd.extend(["-x", "--audio-format", "mp3"])
            logger.info("仅下载音频")
        else:
            # 最佳质量
            cmd.extend(["-f", "bestvideo+bestaudio/best"])
        
        # 添加原始URL
        cmd.append(url)
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 执行下载
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            logger.info("视频下载成功")
            
            # 查找下载的文件
            for file in output_dir.glob("*"):
                if file.is_file() and file.suffix in ['.mp4', '.mkv', '.webm', '.mov']:
                    logger.info(f"找到视频文件: {file}")
                    return file
            
            # 如果是音频文件
            for file in output_dir.glob("*.mp3"):
                if file.is_file():
                    logger.info(f"找到音频文件: {file}")
                    return file
            
            logger.warning("未找到下载的文件")
            return None
            
        else:
            logger.error(f"视频下载失败: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"视频下载过程中发生错误: {e}", exc_info=True)
        return None

def get_video_info(url: str) -> dict:
    """
    获取视频信息
    
    Args:
        url: 视频URL
    
    Returns:
        视频信息字典
    """
    try:
        cmd = ["yt-dlp", "--dump-json", url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        else:
            logger.error(f"获取视频信息失败: {result.stderr}")
            return {}
    except Exception as e:
        logger.error(f"获取视频信息时发生错误: {e}")
        return {}

def list_available_formats(url: str) -> list:
    """
    列出可用格式
    
    Args:
        url: 视频URL
    
    Returns:
        格式列表
    """
    try:
        cmd = ["yt-dlp", "-F", url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            formats = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if line.strip() and 'ID' not in line and '--' not in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        formats.append({
                            'id': parts[0],
                            'format': ' '.join(parts[1:]),
                            'original': line.strip()
                        })
            
            return formats
        else:
            logger.error(f"获取格式列表失败: {result.stderr}")
            return []
    except Exception as e:
        logger.error(f"获取格式列表时发生错误: {e}")
        return []

def check_ytdlp_installed() -> bool:
    """检查yt-dlp是否已安装"""
    try:
        result = subprocess.run(["yt-dlp", "--version"], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ytdlp() -> bool:
    """安装yt-dlp"""
    try:
        logger.info("正在安装yt-dlp...")
        cmd = ["pip", "install", "-U", "yt-dlp"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("yt-dlp安装成功")
            return True
        else:
            logger.error(f"yt-dlp安装失败: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"安装yt-dlp时发生错误: {e}")
        return False

if __name__ == '__main__':
    # 测试代码
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"测试下载: {url}")
        video = download_video(url, Path("./test_output"))
        if video:
            print(f"下载成功: {video}")
        else:
            print("下载失败")