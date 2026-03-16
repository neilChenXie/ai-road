#!/usr/bin/env python3
"""
B站API模块 - 使用Bilibili官方API获取视频信息，绕过412反爬问题
"""

import json
import time
import hashlib
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List
from urllib.parse import urlparse, parse_qs

import requests

logger = logging.getLogger(__name__)

class BilibiliAPI:
    """Bilibili API客户端"""
    
    def __init__(self, session_id: str = None, buvid3: str = None):
        """
        初始化B站API客户端
        
        Args:
            session_id: 会话ID（可选）
            buvid3: B站设备ID（可选）
        """
        self.base_url = "https://api.bilibili.com"
        self.session = requests.Session()
        
        # 设置默认headers，模拟浏览器
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com",
            "Origin": "https://www.bilibili.com",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })
        
        # 如果有cookies，设置它们
        if session_id:
            self.session.cookies.set("SESSDATA", session_id)
        if buvid3:
            self.session.cookies.set("buvid3", buvid3)
    
    def extract_bvid(self, url: str) -> Optional[str]:
        """
        从URL提取BVID
        
        Args:
            url: B站视频URL
            
        Returns:
            BVID字符串，如 "BV12CA1zhEmK"
        """
        try:
            # 处理短链接
            if "b23.tv" in url:
                # 获取重定向后的URL
                response = requests.head(url, allow_redirects=True)
                url = response.url
            
            # 解析URL
            parsed = urlparse(url)
            
            # 从路径中提取BVID
            path = parsed.path
            if "/video/" in path:
                # https://www.bilibili.com/video/BV12CA1zhEmK
                bvid = path.split("/video/")[-1].split("?")[0]
                if bvid.startswith("BV"):
                    return bvid
            
            # 从查询参数中提取
            query_params = parse_qs(parsed.query)
            if "bvid" in query_params:
                return query_params["bvid"][0]
            
            # 尝试其他模式
            for part in path.split("/"):
                if part.startswith("BV") and len(part) == 12:
                    return part
            
            return None
            
        except Exception as e:
            logger.error(f"提取BVID失败: {e}")
            return None
    
    def get_video_info(self, bvid: str) -> Optional[Dict[str, Any]]:
        """
        获取视频基本信息
        
        API: https://api.bilibili.com/x/web-interface/view
        
        Args:
            bvid: 视频BVID
            
        Returns:
            视频信息字典
        """
        try:
            url = f"{self.base_url}/x/web-interface/view"
            params = {"bvid": bvid}
            
            logger.info(f"获取视频信息: {bvid}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") == 0:
                info = data["data"]
                return {
                    "bvid": info.get("bvid"),
                    "avid": info.get("aid"),
                    "title": info.get("title"),
                    "description": info.get("desc"),
                    "duration": info.get("duration"),  # 秒
                    "owner": {
                        "mid": info.get("owner", {}).get("mid"),
                        "name": info.get("owner", {}).get("name"),
                        "face": info.get("owner", {}).get("face"),
                    },
                    "stat": {
                        "view": info.get("stat", {}).get("view"),
                        "danmaku": info.get("stat", {}).get("danmaku"),
                        "reply": info.get("stat", {}).get("reply"),
                        "favorite": info.get("stat", {}).get("favorite"),
                        "coin": info.get("stat", {}).get("coin"),
                        "share": info.get("stat", {}).get("share"),
                        "like": info.get("stat", {}).get("like"),
                    },
                    "pubdate": info.get("pubdate"),  # 时间戳
                    "ctime": info.get("ctime"),
                    "pages": info.get("pages", []),  # 分P信息
                    "subtitle": info.get("subtitle", {}),
                    "staff": info.get("staff", []),
                    "honor_reply": info.get("honor_reply", {}),
                    "raw": info  # 原始数据
                }
            else:
                logger.error(f"API返回错误: {data.get('message')}")
                return None
                
        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            return None
    
    def get_video_play_url(self, bvid: str, cid: int, quality: int = 64) -> Optional[Dict[str, Any]]:
        """
        获取视频播放地址
        
        API: https://api.bilibili.com/x/player/playurl
        
        Args:
            bvid: 视频BVID
            cid: 视频CID（从video_info中获取）
            quality: 视频质量 (64=480p, 80=720p, 112=1080p, 116=1080p60)
            
        Returns:
            播放信息字典
        """
        try:
            url = f"{self.base_url}/x/player/playurl"
            params = {
                "bvid": bvid,
                "cid": cid,
                "qn": quality,
                "fnval": 16,  # 支持flv格式
                "fnver": 0,
                "fourk": 1
            }
            
            logger.info(f"获取播放地址: {bvid}, cid={cid}, quality={quality}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") == 0:
                play_info = data["data"]
                return {
                    "quality": play_info.get("quality"),
                    "format": play_info.get("format"),
                    "timelength": play_info.get("timelength"),
                    "accept_quality": play_info.get("accept_quality"),
                    "accept_description": play_info.get("accept_description"),
                    "durl": play_info.get("durl", []),  # 下载地址
                    "dash": play_info.get("dash"),  # DASH格式
                    "support_formats": play_info.get("support_formats"),
                    "raw": play_info
                }
            else:
                logger.error(f"获取播放地址失败: {data.get('message')}")
                return None
                
        except Exception as e:
            logger.error(f"获取播放地址失败: {e}")
            return None
    
    def get_video_subtitle(self, bvid: str, cid: int) -> Optional[List[Dict[str, Any]]]:
        """
        获取视频字幕
        
        API: https://api.bilibili.com/x/player/v2
        
        Args:
            bvid: 视频BVID
            cid: 视频CID
            
        Returns:
            字幕列表
        """
        try:
            url = f"{self.base_url}/x/player/v2"
            params = {"bvid": bvid, "cid": cid}
            
            logger.info(f"获取字幕: {bvid}, cid={cid}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") == 0:
                subtitle_info = data["data"].get("subtitle", {})
                subtitles = subtitle_info.get("subtitles", [])
                
                # 下载字幕内容
                for subtitle in subtitles:
                    if subtitle.get("subtitle_url"):
                        sub_url = subtitle["subtitle_url"]
                        if sub_url.startswith("//"):
                            sub_url = "https:" + sub_url
                        
                        sub_response = self.session.get(sub_url, timeout=10)
                        if sub_response.status_code == 200:
                            subtitle["content"] = sub_response.json()
                        else:
                            subtitle["content"] = None
                
                return subtitles
            else:
                logger.error(f"获取字幕失败: {data.get('message')}")
                return []
                
        except Exception as e:
            logger.error(f"获取字幕失败: {e}")
            return []
    
    def search_videos(self, keyword: str, page: int = 1, page_size: int = 20) -> Optional[Dict[str, Any]]:
        """
        搜索视频
        
        API: https://api.bilibili.com/x/web-interface/search/type
        
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            
        Returns:
            搜索结果
        """
        try:
            url = f"{self.base_url}/x/web-interface/search/type"
            params = {
                "search_type": "video",
                "keyword": keyword,
                "page": page,
                "page_size": page_size
            }
            
            logger.info(f"搜索视频: {keyword}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") == 0:
                result = data["data"]
                return {
                    "numResults": result.get("numResults"),
                    "numPages": result.get("numPages"),
                    "page": result.get("page"),
                    "result": result.get("result", []),
                    "raw": result
                }
            else:
                logger.error(f"搜索失败: {data.get('message')}")
                return None
                
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return None
    
    def get_user_info(self, mid: int) -> Optional[Dict[str, Any]]:
        """
        获取用户信息
        
        API: https://api.bilibili.com/x/space/acc/info
        
        Args:
            mid: 用户ID
            
        Returns:
            用户信息
        """
        try:
            url = f"{self.base_url}/x/space/acc/info"
            params = {"mid": mid}
            
            logger.info(f"获取用户信息: {mid}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") == 0:
                user_info = data["data"]
                return {
                    "mid": user_info.get("mid"),
                    "name": user_info.get("name"),
                    "sex": user_info.get("sex"),
                    "face": user_info.get("face"),
                    "sign": user_info.get("sign"),
                    "level": user_info.get("level"),
                    "birthday": user_info.get("birthday"),
                    "fans": user_info.get("fans"),
                    "friend": user_info.get("friend"),
                    "attention": user_info.get("attention"),
                    "official": user_info.get("official"),
                    "vip": user_info.get("vip"),
                    "raw": user_info
                }
            else:
                logger.error(f"获取用户信息失败: {data.get('message')}")
                return None
                
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    def get_video_download_urls(self, bvid: str, quality: str = "720p") -> Optional[List[Dict[str, Any]]]:
        """
        获取视频下载地址（整合信息）
        
        Args:
            bvid: 视频BVID
            quality: 视频质量 (480p, 720p, 1080p)
            
        Returns:
            下载地址列表
        """
        try:
            # 1. 获取视频信息
            video_info = self.get_video_info(bvid)
            if not video_info or not video_info.get("pages"):
                logger.error("无法获取视频信息")
                return None
            
            # 2. 获取第一个分P的CID
            first_page = video_info["pages"][0]
            cid = first_page.get("cid")
            if not cid:
                logger.error("无法获取CID")
                return None
            
            # 3. 质量映射
            quality_map = {
                "480p": 64,
                "720p": 80,
                "1080p": 112,
                "1080p60": 116
            }
            qn = quality_map.get(quality, 80)  # 默认720p
            
            # 4. 获取播放地址
            play_info = self.get_video_play_url(bvid, cid, qn)
            if not play_info:
                logger.error("无法获取播放地址")
                return None
            
            # 5. 构建下载地址列表
            download_urls = []
            
            # FLV格式
            if play_info.get("durl"):
                for durl in play_info["durl"]:
                    download_urls.append({
                        "url": durl.get("url"),
                        "size": durl.get("size"),
                        "length": durl.get("length"),
                        "order": durl.get("order"),
                        "format": "flv",
                        "quality": play_info.get("quality"),
                        "backup_url": durl.get("backup_url", [])
                    })
            
            # DASH格式（更现代）
            if play_info.get("dash"):
                dash = play_info["dash"]
                
                # 视频流
                if dash.get("video"):
                    for video in dash["video"]:
                        download_urls.append({
                            "url": video.get("baseUrl"),
                            "size": video.get("size"),
                            "bandwidth": video.get("bandwidth"),
                            "codecs": video.get("codecs"),
                            "width": video.get("width"),
                            "height": video.get("height"),
                            "frame_rate": video.get("frame_rate"),
                            "format": "dash_video",
                            "quality": video.get("id")
                        })
                
                # 音频流
                if dash.get("audio"):
                    for audio in dash["audio"]:
                        download_urls.append({
                            "url": audio.get("baseUrl"),
                            "size": audio.get("size"),
                            "bandwidth": audio.get("bandwidth"),
                            "codecs": audio.get("codecs"),
                            "format": "dash_audio",
                            "sample_rate": audio.get("sample_rate")
                        })
            
            # 6. 获取字幕
            subtitles = self.get_video_subtitle(bvid, cid)
            
            return {
                "video_info": video_info,
                "play_info": play_info,
                "download_urls": download_urls,
                "subtitles": subtitles,
                "recommended_quality": quality,
                "has_audio": any(url["format"] == "dash_audio" for url in download_urls)
            }
            
        except Exception as e:
            logger.error(f"获取下载地址失败: {e}")
            return None
    
    def download_video(self, bvid: str, output_path: str, quality: str = "720p") -> bool:
        """
        下载视频（简化版，实际下载需要更复杂的逻辑）
        
        Args:
            bvid: 视频BVID
            output_path: 输出路径
            quality: 视频质量
            
        Returns:
            是否成功
        """
        try:
            # 获取下载信息
            download_info = self.get_video_download_urls(bvid, quality)
            if not download_info:
                return False
            
            # 这里简化下载逻辑，实际需要：
            # 1. 选择合适的下载地址
            # 2. 处理分段视频合并
            # 3. 下载进度显示
            # 4. 错误重试
            
            logger.info(f"开始下载视频 {bvid}，质量: {quality}")
            logger.info(f"输出路径: {output_path}")
            
            # 选择第一个下载地址
            download_urls = download_info.get("download_urls", [])
            if not download_urls:
                logger.error("没有可用的下载地址")
                return False
            
            # 优先选择DASH视频+音频组合
            dash_video = None
            dash_audio = None
            
            for url_info in download_urls:
                if url_info["format"] == "dash_video":
                    dash_video = url_info
                elif url_info["format"] == "dash_audio":
                    dash_audio = url_info
            
            if dash_video and dash_audio:
                logger.info("找到DASH格式视频和音频流")
                logger.info(f"视频流: {dash_video.get('url')[:60]}...")
                logger.info(f"音频流: {dash_audio.get('url')[:60]}...")
                # 实际下载需要合并视频和音频流
                return True
            
            # 备选：FLV格式
            flv_urls = [u for u in download_urls if u["format"] == "flv"]
            if flv_urls:
                logger.info(f"找到FLV格式视频，{len(flv_urls)}个分段")
                for i, flv in enumerate(flv_urls):
                    logger.info(f"分段{i+1}: {flv.get('url')[:60]}...")
                return True
            
            logger.error("没有支持的下载格式")
            return False
            
        except Exception as e:
            logger.error(f"下载视频失败: {e}")
            return False
    
    def generate_summary(self, bvid: str) -> Optional[Dict[str, Any]]:
        """
        生成视频摘要（基于API信息）
        
        Args:
            bvid: 视频BVID
            
        Returns:
            摘要信息
        """
        try:
            video_info = self.get_video_info(bvid)
            if not video_info:
                return None
            
            # 获取视频播放信息
            play_info = None
            if video_info.get("pages"):
                first_page = video_info["pages"][0]
                cid = first_page.get("cid")
                if cid:
                    play_info = self.get_video_play_url(bvid, cid)
            
            # 构建摘要
            summary = {
                "bvid": video_info.get("bvid"),
                "title": video_info.get("title"),
                "description": video_info.get("description"),
                "duration": video_info.get("duration"),
                "owner": video_info.get("owner", {}).get("name"),
                "stats": video_info.get("stat"),
                "pubdate": datetime.fromtimestamp(video_info.get("pubdate", 0)).strftime("%Y-%m-%d %H:%M:%S") if video_info.get("pubdate") else None,
                "quality_available": play_info.get("accept_description") if play_info else [],
                "pages_count": len(video_info.get("pages", [])),
                "subtitles_available": bool(self.get_video_subtitle(bvid, video_info.get("pages", [{}])[0].get("cid") if video_info.get("pages") else 0)),
                "generated_at": datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return None

# 工具函数
def extract_bvid_from_url(url: str) -> Optional[str]:
    """从URL提取BVID（独立函数）"""
    api = BilibiliAPI()
    return api.extract_bvid(url)

def get_bilibili_video_info(url: str) -> Optional[Dict[str, Any]]:
    """获取B站视频信息（简化接口）"""
    api = BilibiliAPI()
    bvid = api.extract_bvid(url)
    if bvid:
        return api.get_video_info(bvid)
    return None

def can_use_bilibili_api(url: str) -> bool:
    """检查是否可以使用B站API"""
    bvid = extract_bvid_from_url(url)
    return bvid is not None and bvid.startswith("BV")

# 测试代码
if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 测试URL
    test_urls = [
        "https://b23.tv/hHipbJS",
        "https://www.bilibili.com/video/BV12CA1zhEmK",
        "https://www.bilibili.com/video/BV1GJ411x7h7"
    ]
    
    print("🧪 B站API模块测试")
    print("=" * 60)
    
    api = BilibiliAPI()
    
    for url in test_urls:
        print(f"\n测试URL: {url}")
        print("-" * 40)
        
        # 提取BVID
        bvid = api.extract_bvid(url)
        print(f"提取的BVID: {bvid}")
        
        if bvid:
            # 获取视频信息
            info = api.get_video_info(bvid)
            if info:
                print(f"✅ 成功获取视频信息")
                print(f"   标题: {info.get('title', '未知')[:40]}...")
                print(f"   时长: {info.get('duration', 0)}秒")
                print(f"   UP主: {info.get('owner', {}).get('name', '未知')}")
                print(f"   播放量: {info.get('stat', {}).get('view', 0)}")
            else:
                print("❌ 无法获取视频信息")
        else:
            print("❌ 无法提取BVID")