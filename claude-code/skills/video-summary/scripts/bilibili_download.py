#!/usr/bin/env python3
"""
B站视频下载脚本

B站有严格的风控策略，直接使用yt-dlp会触发HTTP 412错误。
此脚本通过B站API方式下载视频，绕过风控。

使用方法：
    python bilibili_download.py "https://www.bilibili.com/video/BVxxxxxx"
    python bilibili_download.py "https://b23.tv/xxxxxx"
"""

import sys
import os
import re
import subprocess
import argparse
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("错误: 需要安装requests库")
    print("请运行: pip install requests")
    sys.exit(1)


class BilibiliDownloader:
    """B站视频下载器"""

    def __init__(self, video_url, output_dir=None, keep_files=False):
        """
        初始化

        Args:
            video_url: B站视频URL (支持 bilibili.com 或 b23.tv 短链接)
            output_dir: 输出目录
            keep_files: 是否保留临时文件
        """
        self.original_url = video_url
        self.output_dir = Path(output_dir) if output_dir else Path("./temp")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.keep_files = keep_files

        # 创建临时工作目录
        self.work_dir = tempfile.mkdtemp(prefix="bilibili_")
        self.work_path = Path(self.work_dir)

        # 视频信息
        self.bvid = None
        self.aid = None
        self.cid = None
        self.title = None

        # 下载的文件
        self.video_file = None
        self.audio_file = None
        self.merged_file = None

        # 请求headers
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.bilibili.com"
        }

        print(f"[初始化] 工作目录: {self.work_dir}")

    def resolve_short_url(self, url):
        """解析短链接"""
        if 'b23.tv' in url:
            print("[解析] 检测到短链接，正在解析...")
            try:
                resp = requests.get(url, headers=self.headers, allow_redirects=True, timeout=10)
                resolved_url = resp.url
                print(f"[解析] 短链接解析为: {resolved_url}")
                return resolved_url
            except Exception as e:
                print(f"[警告] 短链接解析失败: {e}，尝试直接处理")
        return url

    def extract_bvid(self, url):
        """从URL提取BV号"""
        match = re.search(r'(BV[\w]+)', url)
        if match:
            return match.group(1)
        # 尝试提取AV号
        av_match = re.search(r'av(\d+)', url, re.IGNORECASE)
        if av_match:
            return None, int(av_match.group(1))
        return None, None

    def get_video_info(self):
        """获取视频信息 (aid, cid, title)"""
        print("\n[步骤1] 获取视频信息...")

        # 解析短链接
        url = self.resolve_short_url(self.original_url)

        # 提取BV号
        result = self.extract_bvid(url)
        if isinstance(result, tuple):
            self.bvid, aid_from_url = result
            if aid_from_url:
                # 从AV号获取信息
                api_url = "https://api.bilibili.com/x/web-interface/view"
                params = {"aid": aid_from_url}
            else:
                # 从BV号获取信息
                api_url = "https://api.bilibili.com/x/web-interface/view"
                params = {"bvid": self.bvid}
        else:
            self.bvid = result
            api_url = "https://api.bilibili.com/x/web-interface/view"
            params = {"bvid": self.bvid}

        try:
            resp = requests.get(api_url, params=params, headers=self.headers, timeout=10)
            data = resp.json()

            if data['code'] != 0:
                raise RuntimeError(f"API错误: {data['message']}")

            self.aid = data['data']['aid']
            self.cid = data['data']['cid']
            self.title = data['data']['title']
            # 清理文件名中的非法字符
            self.title = re.sub(r'[<>:"/\\|?*]', '_', self.title)

            print(f"✓ 视频标题: {data['data']['title']}")
            print(f"✓ BV号: {data['data']['bvid']}, aid: {self.aid}, cid: {self.cid}")

            return True

        except requests.RequestException as e:
            raise RuntimeError(f"网络请求失败: {e}")

    def get_play_url(self):
        """获取视频和音频的播放地址"""
        print("\n[步骤2] 获取播放地址...")

        api_url = "https://api.bilibili.com/x/player/playurl"
        params = {
            "avid": self.aid,
            "cid": self.cid,
            "qn": 80,  # 80=高清1080P, 64=高清720P, 32=清晰480P
            "fnval": 16,  # 16=DASH格式
            "fnver": 0,
            "fourk": 0
        }

        try:
            resp = requests.get(api_url, params=params, headers=self.headers, timeout=10)
            data = resp.json()

            if data['code'] != 0:
                # 检查是否是会员专属视频
                if data['code'] == -404 or '会员' in data.get('message', ''):
                    raise RuntimeError("此视频可能是会员专属内容，无法下载")
                raise RuntimeError(f"获取播放地址失败: {data['message']}")

            dash = data['data'].get('dash')
            if not dash:
                # 可能是非DASH格式，尝试其他方式
                raise RuntimeError("视频格式不支持，可能需要登录或开通会员")

            # 选择最高清晰度的视频
            video_info = max(dash['video'], key=lambda x: x.get('id', 0))
            video_url = video_info['baseUrl']

            # 选择最高质量的音频
            audio_info = max(dash['audio'], key=lambda x: x.get('id', 0))
            audio_url = audio_info['baseUrl']

            print(f"✓ 视频清晰度: {video_info.get('id')} (DASH)")
            print(f"✓ 音频质量: {audio_info.get('id')}")

            return video_url, audio_url

        except requests.RequestException as e:
            raise RuntimeError(f"网络请求失败: {e}")

    def download_file(self, url, output_path, desc="文件"):
        """下载文件"""
        print(f"[下载] 正在下载{desc}...")

        try:
            # DASH格式需要特殊的headers
            headers = self.headers.copy()
            headers['Range'] = 'bytes=0-'

            resp = requests.get(url, headers=headers, stream=True, timeout=300)
            total = int(resp.headers.get('content-length', 0))

            downloaded = 0
            with open(output_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            progress = downloaded / total * 100
                            print(f"\r[下载] {desc}: {progress:.1f}%", end='', flush=True)

            print(f"\n✓ {desc}下载完成: {output_path}")
            return True

        except requests.RequestException as e:
            raise RuntimeError(f"{desc}下载失败: {e}")

    def download_video(self, video_url, audio_url):
        """下载视频和音频"""
        print("\n[步骤3] 下载视频和音频...")

        self.video_file = self.work_path / "video.m4s"
        self.audio_file = self.work_path / "audio.m4s"

        self.download_file(video_url, self.video_file, "视频")
        self.download_file(audio_url, self.audio_file, "音频")

        return True

    def merge_video_audio(self):
        """使用FFmpeg合并视频和音频"""
        print("\n[步骤4] 合并视频和音频...")

        self.merged_file = self.work_path / f"{self.title}.mp4"

        cmd = [
            "ffmpeg",
            "-i", str(self.video_file),
            "-i", str(self.audio_file),
            "-c:v", "copy",
            "-c:a", "copy",
            "-y",  # 覆盖现有文件
            str(self.merged_file)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                raise RuntimeError(f"合并失败: {result.stderr}")

            if not self.merged_file.exists():
                raise RuntimeError("未找到合并后的视频文件")

            print(f"✓ 合并完成: {self.merged_file}")

            # 复制到输出目录
            final_path = self.output_dir / self.merged_file.name
            shutil.copy2(self.merged_file, final_path)
            print(f"✓ 已保存到: {final_path}")

            return str(final_path)

        except FileNotFoundError:
            raise RuntimeError("FFmpeg未安装。请运行: brew install ffmpeg")
        except subprocess.TimeoutExpired:
            raise RuntimeError("合并超时")

    def cleanup(self):
        """清理临时文件"""
        if not self.keep_files and os.path.exists(self.work_dir):
            try:
                shutil.rmtree(self.work_dir)
                print(f"\n✓ 已删除临时文件")
            except Exception as e:
                print(f"\n⚠ 删除临时文件失败: {e}")

    def run(self):
        """运行完整下载流程"""
        try:
            # 获取视频信息
            self.get_video_info()

            # 获取播放地址
            video_url, audio_url = self.get_play_url()

            # 下载视频和音频
            self.download_video(video_url, audio_url)

            # 合并
            output_file = self.merge_video_audio()

            # 清理临时文件
            self.cleanup()

            print("\n" + "="*50)
            print("===== B站视频下载完成 =====")
            print("="*50)
            print(f"标题: {self.title}")
            print(f"URL: {self.original_url}")
            print(f"输出文件: {output_file}")
            print("="*50)

            return output_file

        except Exception as e:
            print(f"\n✗ 下载失败: {e}", file=sys.stderr)
            self.cleanup()
            return None


def main():
    parser = argparse.ArgumentParser(
        description="B站视频下载工具 (绕过风控)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python bilibili_download.py "https://www.bilibili.com/video/BV1xx411c7mD"
  python bilibili_download.py "https://b23.tv/BV1xx411c7mD"
  python bilibili_download.py "https://..." --output-dir ./videos
        """
    )

    parser.add_argument("url", help="B站视频URL (支持bilibili.com或b23.tv短链接)")
    parser.add_argument("--output-dir", "-o", default=None, help="输出目录 (默认: 当前目录)")
    parser.add_argument("--keep-files", "-k", action="store_true", help="保留临时文件")

    args = parser.parse_args()

    downloader = BilibiliDownloader(
        video_url=args.url,
        output_dir=args.output_dir,
        keep_files=args.keep_files
    )

    result = downloader.run()
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
