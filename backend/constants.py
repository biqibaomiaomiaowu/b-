from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
APP_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_ROOT = APP_ROOT / "frontend"
FRONTEND_DIST_DIR = FRONTEND_ROOT / "dist"
CACHE_CONVERTER_SCRIPT = APP_ROOT / "bilibili_cache_to_mp4.py"
DEFAULT_CACHE_PATH = r"C:\Users\曹乐\Videos\bilibili"
DEFAULT_BBDOWN = "BBDown"
SYSTEM_DOTNET_ROOT = Path(r"C:\Program Files\dotnet")

PROXY_ENV_KEYS = (
    "ALL_PROXY",
    "all_proxy",
    "HTTP_PROXY",
    "http_proxy",
    "HTTPS_PROXY",
    "https_proxy",
    "GIT_HTTP_PROXY",
    "git_http_proxy",
    "GIT_HTTPS_PROXY",
    "git_https_proxy",
)

DEFAULT_NO_PROXY_HOSTS = (
    "localhost",
    "127.0.0.1",
    "::1",
    ".local",
    ".internal",
    "192.168.0.0/16",
    "10.0.0.0/8",
    "172.16.0.0/12",
)

URL_CANDIDATE_PATTERN = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
BILIBILI_ID_PATTERN = re.compile(r"\b(BV[0-9A-Za-z]{10}|av\d+|ep\d+|ss\d+)\b", re.IGNORECASE)
TRAILING_URL_PUNCTUATION = ")]}>】）》」』,，。；;!！?？"

QUALITY_OPTIONS = [
    "自动（最高可用）",
    "8K 超高清",
    "杜比视界",
    "HDR 真彩",
    "4K 超清",
    "1080P 高码率",
    "1080P 60帧",
    "1080P 高清",
    "720P 60帧",
    "720P 高清",
    "480P 清晰",
    "360P 流畅",
]

VALID_QUALITIES = [
    "8K 超高清",
    "杜比视界",
    "HDR 真彩",
    "4K 超清",
    "1080P 高码率",
    "1080P 60帧",
    "1080P 高清",
    "720P 60帧",
    "720P 高清",
    "480P 清晰",
    "360P 流畅",
]

TOOL_LABELS = {
    "bbdown": "BBDown (B站下载核心)",
    "ffmpeg": "FFmpeg (音视频混流/转码)",
    "ffprobe": "FFprobe (媒体信息探测)",
    "mp4box": "MP4Box (备用混流工具)",
    "aria2c": "Aria2c (多线程下载引擎)",
}

TOOL_FIELD_BINDINGS = {
    "bbdown": "bbdown_path",
    "ffmpeg": ["cache_ffmpeg", "ffmpeg_path"],
    "ffprobe": "cache_ffprobe",
    "mp4box": "mp4box_path",
    "aria2c": "aria2c_path",
}

PAGE_LINE_PATTERNS = [
    re.compile(r"^\s*\[P(\d+)\]\s+(.+)$"),
    re.compile(r"^\s*-\s+(\d+)\.\s+(.+)$"),
]
