"""
Dependency Checker - Check and report on required dependencies
"""

import subprocess
import shutil
from typing import Dict
import logging


class DependencyChecker:
    """Check required dependencies"""

    REQUIRED = {
        'python': {'min_version': '3.8', 'command': ['python3', '--version']},
        'ffmpeg': {'min_version': '4.0', 'command': ['ffmpeg', '-version']},
        'yt-dlp': {'min_version': '2023.0', 'command': ['yt-dlp', '--version']},
        'whisper': {'min_version': '20230314', 'command': ['whisper', '--help']},
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def check_all(self) -> Dict:
        """
        Check all dependencies

        Returns:
            Dict with dependency status
        """
        results = {
            'dependencies': {},
            'all_ok': True,
            'missing': [],
            'warnings': []
        }

        for name, config in self.REQUIRED.items():
            status = self._check_dependency(name, config)
            results['dependencies'][name] = status

            if not status['installed']:
                results['all_ok'] = False
                results['missing'].append(name)
            elif not status['version_ok']:
                results['warnings'].append(f"{name} 版本过低: {status['version']}")

        return results

    def _check_dependency(self, name: str, config: Dict) -> Dict:
        """Check single dependency"""
        result = {
            'name': name,
            'installed': False,
            'version': None,
            'version_ok': False,
            'path': None
        }

        # Check if command exists
        cmd = config['command'][0]
        path = shutil.which(cmd)

        if not path:
            return result

        result['installed'] = True
        result['path'] = path

        # Get version
        try:
            proc = subprocess.run(
                config['command'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if proc.returncode == 0:
                version = self._parse_version(proc.stdout)
                result['version'] = version
                result['version_ok'] = True  # Simplified version check

        except Exception as e:
            self.logger.debug(f"获取版本失败: {name} - {e}")

        return result

    def _parse_version(self, output: str) -> str:
        """Parse version from command output"""
        import re
        # Try to find version pattern
        match = re.search(r'(\d+\.\d+\.?\d*)', output)
        if match:
            return match.group(1)
        return 'unknown'

    def print_report(self, results: Dict):
        """Print dependency report"""
        print("\n" + "=" * 50)
        print("依赖检查报告")
        print("=" * 50)

        for name, status in results['dependencies'].items():
            if status['installed']:
                version = status['version'] or 'unknown'
                status_str = f"✅ 已安装 ({version})"
            else:
                status_str = "❌ 未安装"

            print(f"{name:15} {status_str}")

        print("\n" + "-" * 50)

        if results['all_ok']:
            print("✅ 所有依赖已安装")
        else:
            print(f"❌ 缺少依赖: {', '.join(results['missing'])}")
            print("\n安装建议:")
            if 'ffmpeg' in results['missing']:
                print("  brew install ffmpeg")
            if 'yt-dlp' in results['missing']:
                print("  brew install yt-dlp  或  pip install yt-dlp")
            if 'whisper' in results['missing']:
                print("  pipx install openai-whisper")

        if results['warnings']:
            print(f"\n⚠️  警告: {len(results['warnings'])}")
            for w in results['warnings']:
                print(f"  - {w}")
