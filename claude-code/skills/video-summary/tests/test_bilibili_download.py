#!/usr/bin/env python3
"""
B站视频下载脚本单元测试

运行测试：
    cd /path/to/video-summary
    python tests/test_bilibili_download.py
"""

import os
import sys
import unittest
from unittest.mock import patch, Mock
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from bilibili_download import BilibiliDownloader


class TestBilibiliDownloaderInit(unittest.TestCase):
    """测试 BilibiliDownloader 初始化"""

    def setUp(self):
        """每个测试前的设置"""
        self.tmp_path = Path("/tmp/test_bilibili_init")
        self.tmp_path.mkdir(exist_ok=True)

    def tearDown(self):
        """每个测试后的清理"""
        import shutil
        if self.tmp_path.exists():
            shutil.rmtree(self.tmp_path)

    def test_init_with_default_params(self):
        """测试使用默认参数初始化"""
        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/video/BV1test123",
            output_dir=str(self.tmp_path)
        )

        self.assertEqual(downloader.original_url, "https://www.bilibili.com/video/BV1test123")
        self.assertFalse(downloader.keep_files)
        self.assertIsNone(downloader.bvid)
        self.assertIsNone(downloader.aid)
        self.assertIsNone(downloader.cid)
        self.assertIsNone(downloader.title)

        downloader.cleanup()

    def test_init_with_keep_files(self):
        """测试 keep_files 参数"""
        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/video/BV1test123",
            output_dir=str(self.tmp_path),
            keep_files=True
        )

        self.assertTrue(downloader.keep_files)
        downloader.cleanup()

    def test_headers_setup(self):
        """测试请求headers设置"""
        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/video/BV1test123",
            output_dir=str(self.tmp_path)
        )

        self.assertIn("User-Agent", downloader.headers)
        self.assertIn("Referer", downloader.headers)
        self.assertIn("bilibili.com", downloader.headers["Referer"])

        downloader.cleanup()


class TestExtractBvid(unittest.TestCase):
    """测试 BV号提取"""

    def setUp(self):
        self.tmp_path = Path("/tmp/test_bilibili_bvid")
        self.tmp_path.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.tmp_path.exists():
            shutil.rmtree(self.tmp_path)

    def test_extract_bvid_standard_url(self):
        """测试从标准URL提取BV号"""
        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/video/BV1test123",
            output_dir=str(self.tmp_path)
        )

        result = downloader.extract_bvid("https://www.bilibili.com/video/BV1test123")
        self.assertEqual(result, "BV1test123")

        downloader.cleanup()

    def test_extract_bvid_with_extra_params(self):
        """测试从带参数的URL提取BV号"""
        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/video/BV1test123?p=1",
            output_dir=str(self.tmp_path)
        )

        result = downloader.extract_bvid("https://www.bilibili.com/video/BV1test123?p=1")
        self.assertEqual(result, "BV1test123")

        downloader.cleanup()

    def test_extract_av_number(self):
        """测试提取AV号"""
        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/video/av12345678",
            output_dir=str(self.tmp_path)
        )

        result = downloader.extract_bvid("https://www.bilibili.com/video/av12345678")
        self.assertEqual(result, (None, 12345678))

        downloader.cleanup()

    def test_extract_no_valid_id(self):
        """测试无效URL返回None"""
        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/",
            output_dir=str(self.tmp_path)
        )

        result = downloader.extract_bvid("https://www.bilibili.com/")
        self.assertEqual(result, (None, None))

        downloader.cleanup()


class TestResolveShortUrl(unittest.TestCase):
    """测试短链接解析"""

    def setUp(self):
        self.tmp_path = Path("/tmp/test_bilibili_short")
        self.tmp_path.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.tmp_path.exists():
            shutil.rmtree(self.tmp_path)

    @patch('bilibili_download.requests.get')
    def test_resolve_b23_short_url(self, mock_get):
        """测试解析b23.tv短链接"""
        mock_response = Mock()
        mock_response.url = "https://www.bilibili.com/video/BV1resolved"
        mock_get.return_value = mock_response

        downloader = BilibiliDownloader(
            video_url="https://b23.tv/abc123",
            output_dir=str(self.tmp_path)
        )

        result = downloader.resolve_short_url("https://b23.tv/abc123")
        self.assertEqual(result, "https://www.bilibili.com/video/BV1resolved")
        mock_get.assert_called_once()

        downloader.cleanup()

    def test_resolve_non_short_url(self):
        """测试非短链接直接返回"""
        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/video/BV1test123",
            output_dir=str(self.tmp_path)
        )

        result = downloader.resolve_short_url("https://www.bilibili.com/video/BV1test123")
        self.assertEqual(result, "https://www.bilibili.com/video/BV1test123")

        downloader.cleanup()


class TestGetVideoInfo(unittest.TestCase):
    """测试获取视频信息"""

    def setUp(self):
        self.tmp_path = Path("/tmp/test_bilibili_info")
        self.tmp_path.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.tmp_path.exists():
            shutil.rmtree(self.tmp_path)

    @patch('bilibili_download.requests.get')
    def test_get_video_info_success(self, mock_get):
        """测试成功获取视频信息"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "aid": 123456,
                "cid": 789012,
                "title": "测试视频标题",
                "bvid": "BV1test123"
            }
        }
        mock_get.return_value = mock_response

        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/video/BV1test123",
            output_dir=str(self.tmp_path)
        )

        result = downloader.get_video_info()

        self.assertTrue(result)
        self.assertEqual(downloader.aid, 123456)
        self.assertEqual(downloader.cid, 789012)
        self.assertEqual(downloader.title, "测试视频标题")
        self.assertEqual(downloader.bvid, "BV1test123")

        downloader.cleanup()

    @patch('bilibili_download.requests.get')
    def test_get_video_info_api_error(self, mock_get):
        """测试API返回错误"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": -400,
            "message": "请求错误"
        }
        mock_get.return_value = mock_response

        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/video/BV1test123",
            output_dir=str(self.tmp_path)
        )

        with self.assertRaises(RuntimeError):
            downloader.get_video_info()

        downloader.cleanup()

    @patch('bilibili_download.requests.get')
    def test_get_video_info_cleans_title(self, mock_get):
        """测试标题中的非法字符被清理"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "aid": 123456,
                "cid": 789012,
                "title": '测试<视频>标题:非法/字符\\测试',
                "bvid": "BV1test123"
            }
        }
        mock_get.return_value = mock_response

        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/video/BV1test123",
            output_dir=str(self.tmp_path)
        )

        downloader.get_video_info()

        self.assertNotIn('<', downloader.title)
        self.assertNotIn('>', downloader.title)
        self.assertNotIn(':', downloader.title)
        self.assertNotIn('/', downloader.title)
        self.assertNotIn('\\', downloader.title)

        downloader.cleanup()


class TestGetPlayUrl(unittest.TestCase):
    """测试获取播放地址"""

    def setUp(self):
        self.tmp_path = Path("/tmp/test_bilibili_playurl")
        self.tmp_path.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.tmp_path.exists():
            shutil.rmtree(self.tmp_path)

    @patch('bilibili_download.requests.get')
    def test_get_play_url_success(self, mock_get):
        """测试成功获取播放地址"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "dash": {
                    "video": [
                        {"id": 80, "baseUrl": "https://video.url.1"},
                        {"id": 64, "baseUrl": "https://video.url.2"}
                    ],
                    "audio": [
                        {"id": 30280, "baseUrl": "https://audio.url.1"},
                        {"id": 30232, "baseUrl": "https://audio.url.2"}
                    ]
                }
            }
        }
        mock_get.return_value = mock_response

        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/video/BV1test123",
            output_dir=str(self.tmp_path)
        )
        downloader.aid = 123456
        downloader.cid = 789012

        video_url, audio_url = downloader.get_play_url()

        # 应该选择最高清晰度
        self.assertEqual(video_url, "https://video.url.1")
        self.assertEqual(audio_url, "https://audio.url.1")

        downloader.cleanup()

    @patch('bilibili_download.requests.get')
    def test_get_play_url_member_only(self, mock_get):
        """测试会员专属视频"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": -404,
            "message": "会员专属"
        }
        mock_get.return_value = mock_response

        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/video/BV1test123",
            output_dir=str(self.tmp_path)
        )
        downloader.aid = 123456
        downloader.cid = 789012

        with self.assertRaises(RuntimeError):
            downloader.get_play_url()

        downloader.cleanup()


class TestCleanup(unittest.TestCase):
    """测试清理功能"""

    def setUp(self):
        self.tmp_path = Path("/tmp/test_bilibili_cleanup")
        self.tmp_path.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.tmp_path.exists():
            shutil.rmtree(self.tmp_path)

    def test_cleanup_removes_temp_dir(self):
        """测试清理删除临时目录"""
        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/video/BV1test123",
            output_dir=str(self.tmp_path),
            keep_files=False
        )

        work_dir = downloader.work_dir
        self.assertTrue(os.path.exists(work_dir))

        downloader.cleanup()

        self.assertFalse(os.path.exists(work_dir))

    def test_cleanup_keeps_files_when_keep_files_true(self):
        """测试keep_files=True时不删除临时目录"""
        downloader = BilibiliDownloader(
            video_url="https://www.bilibili.com/video/BV1test123",
            output_dir=str(self.tmp_path),
            keep_files=True
        )

        work_dir = downloader.work_dir
        self.assertTrue(os.path.exists(work_dir))

        downloader.cleanup()

        self.assertTrue(os.path.exists(work_dir))

        # 手动清理
        import shutil
        shutil.rmtree(work_dir)


if __name__ == "__main__":
    unittest.main(verbosity=2)
