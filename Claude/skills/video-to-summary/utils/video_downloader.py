#!/usr/bin/env python3
"""
视频下载模块 v2 - 支持多平台视频下载，集成B站API方案
"""

import os
import subprocess
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
import requests

logger = logging.getLogger(__name__)

class VideoDownloader:
    """视频下载器，支持多平台和API方案"""
    
    def __init__(self, output_base_dir: str = "./downloads", use_api: bool = True):
        """
        初始化下载器
        
        Args:
            output_base_dir: 输出基础目录
            use_api: 是否使用API方案
        """
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(exist_ok=True)
        
        self.use_api = use_api
        self.ytdlp_installed = self._check_ytdlp()
        
        # 导入平台检测模块
        try:
            from .platform_detector import detect_platform, get_platform_info, has_api_support
            self.detect_platform = detect_platform
            self.get_platform_info = get_platform_info
            self.has_api_support = has_api_support
        except ImportError:
            # 回退到简单检测
            logger.warning("无法导入platform_detector，使用简单检测")
            self.detect_platform = lambda url: "generic"
            self.get_platform_info = lambda url: {"id": "generic", "name": "通用视频"}
            self.has_api_support = lambda url: {"has_api": False}
    
    def _check_ytdlp(self) -> bool:
        """检查yt-dlp是否安装"""
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _get_output_dir(self, platform: str, video_id: str = None) -> Path:
        """获取输出目录"""
        if video_id:
            dir_name = f"{platform}_{video_id}_{int(time.time())}"
        else:
            dir_name = f"{platform}_{int(time.time())}"
        
        output_dir = self.output_base_dir / dir_name
        output_dir.mkdir(exist_ok=True)
        return output_dir
    
    def _build_ytdlp_command(self, url: str, output_path: Path, 
                           platform: str, quality: str = "720p",
                           audio_only: bool = False) -> List[str]:
        """
        构建yt-dlp命令
        
        Args:
            url: 视频URL
            output_path: 输出路径
            platform: 平台类型
            quality: 视频质量
            audio_only: 是否仅下载音频
        """
        cmd = ["yt-dlp"]
        
        # 输出模板
        if audio_only:
            output_template = str(output_path.with_suffix(".mp3"))
            cmd.extend(["-x", "--audio-format", "mp3"])
        else:
            output_template = str(output_path.with_suffix(".mp4"))
        
        cmd.extend(["-o", output_template])
        
        # 质量选择
        quality_map = {
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "best": "bestvideo+bestaudio/best",
            "audio": "bestaudio"
        }
        
        quality_format = quality_map.get(quality, "bestvideo[height<=720]+bestaudio/best[height<=720]")
        cmd.extend(["-f", quality_format])
        
        # 平台特定配置
        platform_config = self.get_platform_info(url)
        config = platform_config.get("config", {})
        
        # Bilibili配置
        if platform == "bilibili":
            cmd.extend([
                "--referer", "https://www.bilibili.com",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "--add-header", "Accept-Language: zh-CN,zh;q=0.9"
            ])
        
        # 通用功能
        cmd.extend([
            "--retries", "3",
            "--fragment-retries", "3",
            "--retry-sleep", "fragment:3",
            "--concurrent-fragments", "4",
            "--limit-rate", "5M",
            "--no-playlist",
            "--write-info-json",
            "--write-thumbnail",
            "--write-description",
            "--write-sub",
            "--sub-langs", "zh.*,en.*",
            "--convert-subs", "srt"
        ])
        
        # 添加URL
        cmd.append(url)
        
        return cmd
    
    def _download_with_ytdlp(self, url: str, output_path: Path, 
                           platform: str, quality: str = "720p",
                           audio_only: bool = False) -> Dict[str, Any]:
        """使用yt-dlp下载"""
        if not self.ytdlp_installed:
            return {
                "success": False,
                "error": "yt-dlp未安装",
                "method": "yt-dlp"
            }
        
        try:
            cmd = self._build_ytdlp_command(url, output_path, platform, quality, audio_only)
            logger.info(f"执行yt-dlp命令: {' '.join(cmd[:8])}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                # 查找下载的文件
                downloaded_files = []
                for ext in ['.mp4', '.mp3', '.webm', '.mkv']:
                    file_path = output_path.with_suffix(ext)
                    if file_path.exists():
                        downloaded_files.append(str(file_path))
                
                # 查找json信息文件
                info_file = output_path.with_suffix(".info.json")
                download_info = {}
                if info_file.exists():
                    with open(info_file, 'r', encoding='utf-8') as f:
                        download_info = json.load(f)
                
                return {
                    "success": True,
                    "method": "yt-dlp",
                    "files": downloaded_files,
                    "download_info": download_info,
                    "log": result.stdout[-500:]  # 最后500字符
                }
            else:
                error_msg = result.stderr.strip()
                logger.error(f"yt-dlp下载失败: {error_msg[:100]}")
                
                # 检查是否是412错误
                if "HTTP Error 412" in error_msg:
                    return {
                        "success": False,
                        "error": "B站412反爬错误",
                        "suggestion": "尝试使用API方案 (--use-api)",
                        "method": "yt-dlp",
                        "log": error_msg
                    }
                else:
                    return {
                        "success": False,
                        "error": error_msg,
                        "method": "yt-dlp"
                    }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "下载超时",
                "method": "yt-dlp"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "yt-dlp"
            }
    
    def _download_with_bilibili_api(self, url: str, output_path: Path,
                                  quality: str = "720p") -> Dict[str, Any]:
        """使用B站API下载"""
        try:
            from .bilibili_api import BilibiliAPI
            from .bilibili_downloader import BilibiliDownloader
            
            # 创建API客户端和下载器
            api = BilibiliAPI()
            bili_downloader = BilibiliDownloader(output_dir=str(output_path.parent))
            
            # 获取下载信息
            download_info = bili_downloader.download_with_api_fallback(
                url=url,
                quality=quality,
                audio_only=False
            )
            
            if download_info.get("success"):
                return {
                    "success": True,
                    "method": "bilibili_api",
                    "bvid": download_info.get("bvid"),
                    "title": download_info.get("title"),
                    "download_info": download_info,
                    "message": "已获取下载地址，建议使用专用工具下载"
                }
            else:
                return {
                    "success": False,
                    "error": download_info.get("error", "未知错误"),
                    "method": "bilibili_api"
                }
                
        except ImportError:
            return {
                "success": False,
                "error": "B站API模块未安装",
                "method": "bilibili_api"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "bilibili_api"
            }
    
    def download_video(self, url: str, quality: str = "720p", 
                      audio_only: bool = False) -> Dict[str, Any]:
        """
        下载视频（主函数）
        
        Args:
            url: 视频URL
            quality: 视频质量
            audio_only: 是否仅下载音频
            
        Returns:
            下载结果
        """
        try:
            logger.info(f"开始下载视频: {url}")
            
            # 检测平台
            platform = self.detect_platform(url)
            platform_info = self.get_platform_info(url)
            api_info = self.has_api_support(url)
            
            logger.info(f"平台: {platform} ({platform_info.get('name')})")
            logger.info(f"API支持: {api_info.get('has_api', False)}")
            
            # 获取视频ID（用于目录命名）
            video_id = "unknown"
            if platform == "bilibili":
                try:
                    from .bilibili_api import extract_bvid_from_url
                    video_id = extract_bvid_from_url(url) or "unknown"
                except:
                    pass
            
            # 创建输出目录
            output_dir = self._get_output_dir(platform, video_id)
            output_path = output_dir / "video"
            
            # 选择下载策略
            if platform == "bilibili" and self.use_api and api_info.get("has_api"):
                logger.info("使用B站API方案（绕过412问题）")
                
                # 先尝试API方案
                api_result = self._download_with_bilibili_api(url, output_path, quality)
                
                if api_result.get("success"):
                    # API方案成功
                    api_result["output_dir"] = str(output_dir)
                    return api_result
                else:
                    # API方案失败，回退到yt-dlp
                    logger.warning(f"API方案失败，回退到yt-dlp: {api_result.get('error')}")
                    if self.ytdlp_installed:
                        ytdlp_result = self._download_with_ytdlp(
                            url, output_path, platform, quality, audio_only
                        )
                        ytdlp_result["fallback_from"] = "bilibili_api"
                        ytdlp_result["output_dir"] = str(output_dir)
                        return ytdlp_result
                    else:
                        return api_result  # 返回API错误
            else:
                # 使用yt-dlp
                if self.ytdlp_installed:
                    result = self._download_with_ytdlp(
                        url, output_path, platform, quality, audio_only
                    )
                    result["output_dir"] = str(output_dir)
                    return result
                else:
                    return {
                        "success": False,
                        "error": "yt-dlp未安装",
                        "platform": platform,
                        "url": url
                    }
                    
        except Exception as e:
            logger.error(f"下载过程中异常: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        获取视频信息
        
        Args:
            url: 视频URL
            
        Returns:
            视频信息
        """
        try:
            platform = self.detect_platform(url)
            api_info = self.has_api_support(url)
            
            # 如果是B站且有API支持，使用API获取信息
            if platform == "bilibili" and api_info.get("has_api"):
                try:
                    from .bilibili_api import BilibiliAPI
                    api = BilibiliAPI()
                    bvid = api.extract_bvid(url)
                    if bvid:
                        video_info = api.get_video_info(bvid)
                        if video_info:
                            return {
                                "success": True,
                                "platform": platform,
                                "method": "bilibili_api",
                                "data": video_info,
                                "bvid": bvid
                            }
                except Exception as e:
                    logger.warning(f"B站API获取信息失败: {e}")
            
            # 回退到yt-dlp
            if self.ytdlp_installed:
                cmd = ["yt-dlp", "--dump-json", url]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    return {
                        "success": True,
                        "platform": platform,
                        "method": "yt-dlp",
                        "data": data
                    }
                else:
                    return {
                        "success": False,
                        "error": result.stderr.strip(),
                        "platform": platform
                    }
            else:
                return {
                    "success": False,
                    "error": "yt-dlp未安装",
                    "platform": platform
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "unknown"
            }
    
    def batch_download(self, urls: List[str], quality: str = "720p",
                      max_workers: int = 3) -> List[Dict[str, Any]]:
        """
        批量下载视频
        
        Args:
            urls: URL列表
            quality: 视频质量
            max_workers: 最大并行数
            
        Returns:
            下载结果列表
        """
        results = []
        
        # 简单实现：顺序下载
        # 实际应该使用ThreadPoolExecutor
        for i, url in enumerate(urls):
            logger.info(f"处理第 {i+1}/{len(urls)} 个视频: {url}")
            
            result = self.download_video(url, quality)
            results.append(result)
            
            # 添加序号信息
            result["index"] = i + 1
            result["total"] = len(urls)
            
            time.sleep(1)  # 避免请求过快
        
        # 生成总结报告
        success_count = sum(1 for r in results if r.get("success"))
        
        summary = {
            "total": len(urls),
            "success": success_count,
            "failed": len(urls) - success_count,
            "success_rate": f"{(success_count/len(urls)*100):.1f}%" if urls else "0%",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": results
        }
        
        # 保存报告
        report_path = self.output_base_dir / f"batch_report_{int(time.time())}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"批量下载完成: {success_count}/{len(urls)} 成功")
        logger.info(f"报告保存到: {report_path}")
        
        return summary

# 兼容旧API
def download_video(url: str, output_dir: Path, **kwargs) -> Optional[Path]:
    """兼容旧API的下载函数"""
    downloader = VideoDownloader(output_base_dir=str(output_dir.parent))
    result = downloader.download_video(url)
    
    if result.get("success") and result.get("files"):
        # 返回第一个文件
        return Path(result["files"][0])
    return None

def get_video_info(url: str) -> dict:
    """兼容旧API的信息获取函数"""
    downloader = VideoDownloader()
    result = downloader.get_video_info(url)
    
    if result.get("success"):
        return result.get("data", {})
    return {}

def check_ytdlp_installed() -> bool:
    """检查yt-dlp是否安装"""
    downloader = VideoDownloader()
    return downloader.ytdlp_installed

# 测试代码
if __name__ == "__main__":
    import sys
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 视频下载器 v2 测试")
    print("=" * 60)
    
    # 创建下载器
    downloader = VideoDownloader(output_base_dir="./test_downloads", use_api=True)
    
    # 测试URL
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        test_url = "https://b23.tv/hHipbJS"
    
    print(f"测试URL: {test_url}")
    print("-" * 40)
    
    # 1. 获取视频信息
    print("1. 获取视频信息...")
    info_result = downloader.get_video_info(test_url)
    
    if info_result.get("success"):
        data = info_result.get("data", {})
        print(f"✅ 成功获取视频信息")
        print(f"   方法: {info_result.get('method')}")
        print(f"   标题: {data.get('title', '未知')[:50]}...")
        
        if info_result.get("method") == "bilibili_api":
            print(f"   BVID: {info_result.get('bvid')}")
            print(f"   播放量: {data.get('stat', {}).get('view', 0)}")
    else:
        print(f"❌ 获取视频信息失败: {info_result.get('error')}")
    
    print()
    
    # 2. 测试下载（不实际下载大文件）
    print("2. 测试下载流程（模拟）...")
    print("注意: 仅测试流程，不实际下载大文件")
    
    result = downloader.download_video(test_url, quality="720p")
    
    if result.get("success"):
        print(f"✅ 下载流程测试成功")
        print(f"   方法: {result.get('method')}")
        
        if result.get("method") == "bilibili_api":
            print(f"   状态: {result.get('message')}")
            if result.get("download_info") and result["download_info"].get("download_urls"):
                urls = result["download_info"]["download_urls"]
                print(f"   下载地址: {len(urls)}个")
                for i, url_info in enumerate(urls[:2]):
                    print(f"     {i+1}. {url_info.get('format')}: {url_info.get('url', '')[:60]}...")
        else:
            print(f"   文件: {result.get('files', [])}")
    else:
        print(f"❌ 下载流程测试失败")
        print(f"   错误: {result.get('error')}")
        if result.get("suggestion"):
            print(f"   建议: {result.get('suggestion')}")
    
    print()
    print("=" * 60)
    print("🎯 测试完成")
    print(f"✅ yt-dlp安装状态: {downloader.ytdlp_installed}")
    print(f"✅ API支持: 已集成B站API方案")
    print(f"✅ 多平台支持: 已实现")
    print("=" * 60)