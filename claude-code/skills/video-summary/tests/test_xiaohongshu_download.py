#!/usr/bin/env python3
"""
小红书视频下载和总结脚本单元测试

运行测试：
    cd /path/to/video-summary
    python tests/test_xiaohongshu_download.py
"""

import os
import sys
import unittest
from unittest.mock import patch, Mock
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from xiaohongshu_download_and_summarize import XiaohongshuSummarizer


class TestXiaohongshuSummarizerInit(unittest.TestCase):
    """测试 XiaohongshuSummarizer 初始化"""

    def setUp(self):
        """每个测试前的设置"""
        self.tmp_path = Path("/tmp/test_xiaohongshu_init")
        self.tmp_path.mkdir(exist_ok=True)

    def tearDown(self):
        """每个测试后的清理"""
        import shutil
        if self.tmp_path.exists():
            shutil.rmtree(self.tmp_path)

    def test_init_with_default_params(self):
        """测试使用默认参数初始化"""
        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path)
        )

        self.assertEqual(summarizer.video_url, "https://www.xiaohongshu.com/explore/test123")
        self.assertEqual(summarizer.model, "base")
        self.assertEqual(summarizer.language, "zh")
        self.assertFalse(summarizer.keep_files)
        self.assertIsNone(summarizer.video_file)
        self.assertIsNone(summarizer.audio_file)
        self.assertIsNone(summarizer.transcript_file)
        self.assertIsNone(summarizer.summary_file)

        summarizer.cleanup()

    def test_init_with_custom_params(self):
        """测试使用自定义参数初始化"""
        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            model="medium",
            language="en",
            keep_files=True,
            output_dir=str(self.tmp_path)
        )

        self.assertEqual(summarizer.model, "medium")
        self.assertEqual(summarizer.language, "en")
        self.assertTrue(summarizer.keep_files)

        summarizer.cleanup()

    def test_output_dir_created(self):
        """测试输出目录创建"""
        new_dir = self.tmp_path / "new_output_dir"
        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(new_dir)
        )

        self.assertTrue(new_dir.exists())

        summarizer.cleanup()


class TestSummarizeContent(unittest.TestCase):
    """测试内容总结功能"""

    def setUp(self):
        self.tmp_path = Path("/tmp/test_xiaohongshu_summarize")
        self.tmp_path.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.tmp_path.exists():
            shutil.rmtree(self.tmp_path)

    def test_summarize_basic_content(self):
        """测试基本内容总结"""
        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path)
        )

        transcript = "这是第一句话。这是第二句话。这是第三句话。这是第四句话。这是第五句话。"
        summary = summarizer.summarize_content(transcript)

        # 总结应该比原文短
        self.assertLessEqual(len(summary), len(transcript))
        # 总结应该以句号结尾
        self.assertTrue(summary.endswith("。"))

        summarizer.cleanup()

    def test_summarize_empty_content(self):
        """测试空内容"""
        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path)
        )

        transcript = ""
        summary = summarizer.summarize_content(transcript)

        self.assertEqual(summary, "")

        summarizer.cleanup()

    def test_summarize_single_sentence(self):
        """测试单句内容"""
        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path)
        )

        transcript = "这是唯一的一句话"
        summary = summarizer.summarize_content(transcript)

        # 单句内容会添加句号
        self.assertIn(transcript, summary)

        summarizer.cleanup()

    def test_summarize_content_without_period(self):
        """测试没有句号的内容"""
        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path)
        )

        transcript = "这是第一句话 这是第二句话 这是第三句话"
        summary = summarizer.summarize_content(transcript)

        # 没有句号的内容，split会返回整个字符串作为一个元素
        self.assertIsInstance(summary, str)

        summarizer.cleanup()

    def test_summarize_long_content(self):
        """测试长内容总结"""
        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path)
        )

        # 创建长文本
        sentences = [f"这是第{i}句话，包含一些内容。" for i in range(1, 21)]
        transcript = "".join(sentences)

        summary = summarizer.summarize_content(transcript)

        # 总结应该比原文短
        self.assertLess(len(summary), len(transcript))
        # 总结应该是原文的20-30%左右
        ratio = len(summary) / len(transcript)
        self.assertLessEqual(ratio, 0.35)  # 允许一些误差

        summarizer.cleanup()


class TestSaveResults(unittest.TestCase):
    """测试保存结果功能"""

    def setUp(self):
        self.tmp_path = Path("/tmp/test_xiaohongshu_save")
        self.tmp_path.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.tmp_path.exists():
            shutil.rmtree(self.tmp_path)

    def test_save_results_creates_files(self):
        """测试保存结果创建文件"""
        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path)
        )

        transcript_text = "这是转录的测试文本。"
        summary_text = "这是总结的测试文本。"

        transcript_file, summary_file = summarizer.save_results(transcript_text, summary_text)

        # 检查文件是否存在
        self.assertTrue(os.path.exists(transcript_file))
        self.assertTrue(os.path.exists(summary_file))

        # 检查文件内容
        with open(transcript_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(transcript_text, content)
            self.assertIn("https://www.xiaohongshu.com/explore/test123", content)

        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(summary_text, content)

        summarizer.cleanup()

    def test_save_results_filename_format(self):
        """测试文件名格式"""
        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path)
        )

        transcript_file, summary_file = summarizer.save_results("测试", "测试")

        # 检查文件名格式
        self.assertIn("transcript_", transcript_file)
        self.assertIn("summary_", summary_file)
        self.assertTrue(transcript_file.endswith(".txt"))
        self.assertTrue(summary_file.endswith(".txt"))

        summarizer.cleanup()


class TestCleanup(unittest.TestCase):
    """测试清理功能"""

    def setUp(self):
        self.tmp_path = Path("/tmp/test_xiaohongshu_cleanup")
        self.tmp_path.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.tmp_path.exists():
            shutil.rmtree(self.tmp_path)

    def test_cleanup_removes_temp_dir(self):
        """测试清理删除临时目录"""
        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path),
            keep_files=False
        )

        work_dir = summarizer.work_dir
        self.assertTrue(os.path.exists(work_dir))

        summarizer.cleanup()

        self.assertFalse(os.path.exists(work_dir))

    def test_cleanup_keeps_files_when_keep_files_true(self):
        """测试keep_files=True时不删除临时目录"""
        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path),
            keep_files=True
        )

        work_dir = summarizer.work_dir
        self.assertTrue(os.path.exists(work_dir))

        summarizer.cleanup()

        self.assertTrue(os.path.exists(work_dir))

        # 手动清理
        import shutil
        shutil.rmtree(work_dir)


class TestDownloadVideo(unittest.TestCase):
    """测试视频下载功能"""

    def setUp(self):
        self.tmp_path = Path("/tmp/test_xiaohongshu_download")
        self.tmp_path.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.tmp_path.exists():
            shutil.rmtree(self.tmp_path)

    @patch('xiaohongshu_download_and_summarize.subprocess.run')
    def test_download_video_success(self, mock_run):
        """测试成功下载视频"""
        mock_run.return_value = Mock(returncode=0, stderr="")

        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path)
        )

        # 创建一个模拟的视频文件
        video_path = summarizer.work_path / "video.mp4"
        video_path.touch()

        result = summarizer.download_video()

        self.assertTrue(result)
        self.assertIsNotNone(summarizer.video_file)
        mock_run.assert_called_once()

        summarizer.cleanup()

    @patch('xiaohongshu_download_and_summarize.subprocess.run')
    def test_download_video_failure(self, mock_run):
        """测试下载失败"""
        mock_run.return_value = Mock(returncode=1, stderr="下载错误")

        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path)
        )

        with self.assertRaises(RuntimeError):
            summarizer.download_video()

        summarizer.cleanup()


class TestExtractAudio(unittest.TestCase):
    """测试音频提取功能"""

    def setUp(self):
        self.tmp_path = Path("/tmp/test_xiaohongshu_audio")
        self.tmp_path.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.tmp_path.exists():
            shutil.rmtree(self.tmp_path)

    @patch('xiaohongshu_download_and_summarize.subprocess.run')
    def test_extract_audio_success(self, mock_run):
        """测试成功提取音频"""
        mock_run.return_value = Mock(returncode=0, stderr="")

        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path)
        )

        # 创建模拟的视频文件
        summarizer.video_file = summarizer.work_path / "video.mp4"
        summarizer.video_file.touch()

        # 预先创建音频文件（模拟ffmpeg输出）
        expected_audio = summarizer.work_path / "audio.mp3"
        expected_audio.touch()

        result = summarizer.extract_audio()

        self.assertTrue(result)
        self.assertIsNotNone(summarizer.audio_file)

        summarizer.cleanup()

    @patch('xiaohongshu_download_and_summarize.subprocess.run')
    def test_extract_audio_ffmpeg_not_found(self, mock_run):
        """测试FFmpeg未安装"""
        mock_run.side_effect = FileNotFoundError()

        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path)
        )

        summarizer.video_file = summarizer.work_path / "video.mp4"
        summarizer.video_file.touch()

        with self.assertRaises(RuntimeError):
            summarizer.extract_audio()

        summarizer.cleanup()


class TestTranscribeAudio(unittest.TestCase):
    """测试音频转录功能"""

    def setUp(self):
        self.tmp_path = Path("/tmp/test_xiaohongshu_transcribe")
        self.tmp_path.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.tmp_path.exists():
            shutil.rmtree(self.tmp_path)

    @patch('xiaohongshu_download_and_summarize.subprocess.run')
    def test_transcribe_audio_success(self, mock_run):
        """测试成功转录"""
        mock_run.return_value = Mock(returncode=0, stderr="")

        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path)
        )

        # 创建模拟的音频文件和转录结果
        summarizer.audio_file = summarizer.work_path / "audio.mp3"
        summarizer.audio_file.touch()

        transcript_path = summarizer.work_path / "audio.txt"
        transcript_path.write_text("这是转录的测试文本。", encoding='utf-8')

        result = summarizer.transcribe_audio()

        self.assertEqual(result, "这是转录的测试文本。")

        summarizer.cleanup()

    @patch('xiaohongshu_download_and_summarize.subprocess.run')
    def test_transcribe_audio_whisper_not_found(self, mock_run):
        """测试Whisper未安装"""
        mock_run.side_effect = FileNotFoundError()

        summarizer = XiaohongshuSummarizer(
            video_url="https://www.xiaohongshu.com/explore/test123",
            output_dir=str(self.tmp_path)
        )

        summarizer.audio_file = summarizer.work_path / "audio.mp3"
        summarizer.audio_file.touch()

        with self.assertRaises(RuntimeError):
            summarizer.transcribe_audio()

        summarizer.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
