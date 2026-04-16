"""
测试配置文件

运行所有测试：
    cd /path/to/video-summary
    python -m unittest discover -s tests -v

运行单个测试文件：
    python tests/test_bilibili_download.py
    python tests/test_xiaohongshu_download.py
"""

import sys
from pathlib import Path

# 确保可以导入scripts目录下的模块
scripts_path = Path(__file__).parent.parent / "scripts"
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))
