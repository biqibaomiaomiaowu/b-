from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class CacheRunPayload(BaseModel):
    input_path: str
    output: str = ""
    ffmpeg: str = ""
    ffprobe: str = ""
    force: bool = False
    dry_run: bool = False

class ToolDetectPayload(BaseModel):
    bbdown_path: str = ""
    cache_ffmpeg: str = ""
    cache_ffprobe: str = ""
    ffmpeg_path: str = ""
    mp4box_path: str = ""
    aria2c_path: str = ""

class LoginStatusPayload(BaseModel):
    bbdown_path: str = ""

class LoginStartPayload(BaseModel):
    bbdown_path: str = ""
    mode: str = "web"

class CommonDownloadPayload(BaseModel):
    bbdown_path: str = ""
    output: str = ""
    page_spec: str = ""
    show_all_pages: bool = False
    download_mode: str = ""
    api_mode: str = ""
    encoding_priority: str = ""
    language: str = ""
    user_agent: str = ""
    cookie: str = ""
    access_token: str = ""
    download_danmaku: bool = False
    skip_subtitle: bool = False
    skip_cover: bool = False
    use_aria2c: bool = False
    use_mp4box: bool = False
    skip_mux: bool = False
    hide_streams: bool = False
    debug_mode: bool = False
    download_ai_subtitle: bool = False
    video_ascending: bool = False
    audio_ascending: bool = False
    allow_pcdn: bool = False
    save_archives_to_file: bool = False
    ffmpeg_path: str = ""
    mp4box_path: str = ""
    aria2c_path: str = ""
    aria2c_args: str = ""
    delay_per_page: str = ""
    file_pattern: str = ""
    multi_file_pattern: str = ""
    work_dir_override: str = ""
    upos_host: str = ""
    host: str = ""
    ep_host: str = ""
    area: str = ""
    config_file: str = ""
    extra_args: str = ""

class UrlInfoPayload(CommonDownloadPayload):
    url: str

class UrlDownloadPayload(CommonDownloadPayload):
    url: str
    quality: str = ""

class UrlBatchPayload(CommonDownloadPayload):
    urls_text: str
    quality: str = ""
    batch_continue_on_error: bool = False
