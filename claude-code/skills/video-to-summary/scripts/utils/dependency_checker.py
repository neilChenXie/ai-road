"""
Dependency checking and management
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class DependencyChecker:
    """Check for required system dependencies"""

    REQUIRED_COMMANDS = {
        'python3': 'Python 3',
        'ffmpeg': 'FFmpeg (for audio extraction)',
        'yt-dlp': 'yt-dlp (for video download)',
        'whisper': 'OpenAI Whisper (for speech recognition)',
    }

    REQUIRED_PYTHON_PACKAGES = [
        'requests',
        'beautifulsoup4',
        'pyyaml',
    ]

    def __init__(self):
        self.missing_commands: List[str] = []
        self.missing_packages: List[str] = []
        self.python_version: str = self._get_python_version()

    def _get_python_version(self) -> str:
        """Get Python version"""
        try:
            result = subprocess.run(
                ['python3', '--version'],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except Exception:
            return "Unknown"

    def check_python_version(self) -> Tuple[bool, str]:
        """Check if Python version is >= 3.8"""
        try:
            version = sys.version_info
            if version.major < 3 or (version.major == 3 and version.minor < 8):
                return False, f"Python 3.8+ required, found {version.major}.{version.minor}"
            return True, f"Python {version.major}.{version.minor}.{version.micro}"
        except Exception as e:
            return False, f"Error checking Python version: {e}"

    def check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            result = subprocess.run(
                ['which', command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_python_package(self, package: str) -> bool:
        """Check if a Python package is installed"""
        try:
            subprocess.run(
                ['python3', '-c', f'import {package}'],
                capture_output=True,
                text=True
            )
            return True
        except Exception:
            return False

    def check_all(self) -> Dict[str, any]:
        """Check all dependencies"""
        results = {
            'python': {},
            'commands': {},
            'packages': {},
            'all_ok': True
        }

        # Check Python version
        python_ok, python_msg = self.check_python_version()
        results['python'] = {
            'ok': python_ok,
            'message': python_msg
        }
        if not python_ok:
            results['all_ok'] = False

        # Check commands
        for cmd, desc in self.REQUIRED_COMMANDS.items():
            ok = self.check_command(cmd)
            results['commands'][cmd] = {
                'ok': ok,
                'description': desc
            }
            if not ok:
                self.missing_commands.append(cmd)
                results['all_ok'] = False

        # Check Python packages
        for pkg in self.REQUIRED_PYTHON_PACKAGES:
            ok = self.check_python_package(pkg)
            results['packages'][pkg] = {'ok': ok}
            if not ok:
                self.missing_packages.append(pkg)
                results['all_ok'] = False

        return results

    def print_report(self, results: Dict[str, any]):
        """Print dependency check report"""
        print("\n=== Dependency Check Report ===\n")

        # Python version
        python_result = results['python']
        status = "✓" if python_result['ok'] else "✗"
        print(f"{status} Python: {python_result['message']}")

        # Commands
        print("\nCommands:")
        for cmd, info in results['commands'].items():
            status = "✓" if info['ok'] else "✗"
            print(f"  {status} {cmd:12s} - {info['description']}")

        # Packages
        print("\nPython packages:")
        for pkg, info in results['packages'].items():
            status = "✓" if info['ok'] else "✗"
            print(f"  {status} {pkg}")

        # Summary
        print("\n" + "="*40)
        if results['all_ok']:
            print("✓ All dependencies are installed!")
        else:
            print("✗ Some dependencies are missing.")
            print("\nTo install missing dependencies:")
            print("  bash install.sh")

    def get_fix_commands(self) -> List[str]:
        """Get commands to fix missing dependencies"""
        commands = []

        if not self.check_python_version()[0]:
            commands.append("# Install Python 3.8+")
            commands.append("brew install python3  # macOS")
            commands.append("# or")
            commands.append("sudo apt install python3  # Ubuntu/Debian")
            commands.append("")

        if 'ffmpeg' in self.missing_commands:
            commands.append("# Install FFmpeg")
            commands.append("brew install ffmpeg  # macOS")
            commands.append("# or")
            commands.append("sudo apt-get install ffmpeg  # Ubuntu/Debian")
            commands.append("")

        if 'yt-dlp' in self.missing_commands:
            commands.append("# Install yt-dlp")
            commands.append("brew install yt-dlp  # macOS")
            commands.append("# or")
            commands.append("pip3 install yt-dlp  # Linux")
            commands.append("")

        if 'whisper' in self.missing_commands:
            commands.append("# Install Whisper (requires pipx)")
            commands.append("pipx install openai-whisper")
            commands.append("pipx ensurepath  # Add to PATH")
            commands.append("")

        if self.missing_packages:
            commands.append("# Install Python packages")
            commands.append("pip3 install --break-system-packages -r requirements.txt")
            commands.append("# or use a virtual environment")

        return commands


if __name__ == '__main__':
    checker = DependencyChecker()
    results = checker.check_all()
    checker.print_report(results)
