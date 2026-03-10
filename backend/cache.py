import sys
import subprocess
from pathlib import Path
from backend.constants import CACHE_CONVERTER_SCRIPT, DEFAULT_CACHE_PATH

def get_cache_converter_script() -> Path:
    # 兼容处理：确保我们能够找到 cache_to_mp4 的脚本，如果在打包或者重构结构下
    p = Path(__file__).resolve().parent.parent / "bilibili_cache_to_mp4.py"
    if p.exists():
        return p
    return CACHE_CONVERTER_SCRIPT

def run_cache_conversion(payload: dict) -> dict[str, object]:
    input_path = payload.get("input_path", "").strip() or DEFAULT_CACHE_PATH
    output = payload.get("output", "").strip()
    ffmpeg = payload.get("ffmpeg", "").strip()
    ffprobe = payload.get("ffprobe", "").strip()
    force = payload.get("force", False)
    dry_run = payload.get("dry_run", False)

    script_path = get_cache_converter_script()
    command = [sys.executable, str(script_path)]

    if ffmpeg:
        command.extend(["--ffmpeg", ffmpeg])
    if ffprobe:
        command.extend(["--ffprobe", ffprobe])
    if output:
        command.extend(["--output", output])
    if force:
        command.append("--force")
    if dry_run:
        command.append("--dry-run")

    command.append(input_path)

    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        return {
            "command": " ".join(command),
            "returncode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
        }
    except Exception as e:
        return {
            "command": " ".join(command),
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
        }
