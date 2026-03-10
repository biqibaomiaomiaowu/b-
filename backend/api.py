from fastapi import APIRouter
from datetime import datetime

from backend.models import (
    CacheRunPayload,
    ToolDetectPayload,
    LoginStatusPayload,
    LoginStartPayload,
    UrlInfoPayload,
    UrlDownloadPayload,
    UrlBatchPayload
)
from backend.tools import detect_tool_paths
from backend.cache import run_cache_conversion
from backend.bilibili import (
    normalize_video_target,
    build_bbdown_command,
    run_subprocess,
    extract_page_items_from_text,
    extract_qualities,
    fetch_page_items_from_bilibili_api,
    run_batch_downloads,
    get_bbdown_login_status,
    start_bbdown_login_process,
    clear_bbdown_login_data
)
from backend.constants import DEFAULT_BBDOWN, DEFAULT_CACHE_PATH, QUALITY_OPTIONS

router = APIRouter(prefix="/api")

@router.get("/bootstrap")
def api_bootstrap():
    return {
        "default_cache_path": DEFAULT_CACHE_PATH,
        "default_bbdown": DEFAULT_BBDOWN,
        "quality_options": QUALITY_OPTIONS,
        "server_url": "",  # Frontend can derive this
    }

@router.post("/tool-detect")
def api_tool_detect(payload: ToolDetectPayload):
    return detect_tool_paths(payload.model_dump())

@router.post("/cache-run")
def api_cache_run(payload: CacheRunPayload):
    result = run_cache_conversion(payload.model_dump())
    result["finished_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return result

@router.post("/login-status")
def api_login_status(payload: LoginStatusPayload):
    return get_bbdown_login_status(payload.bbdown_path)

@router.post("/login-start")
def api_login_start(payload: LoginStartPayload):
    return start_bbdown_login_process(payload.bbdown_path, payload.mode)

@router.post("/login-clear")
def api_login_clear(payload: LoginStatusPayload):
    return clear_bbdown_login_data(payload.bbdown_path)

@router.post("/url-info")
def api_url_info(payload: UrlInfoPayload):
    url = normalize_video_target(payload.url)
    if not url:
        return {"error": "Invalid URL"}

    pdict = payload.model_dump()
    command, work_dir, _ = build_bbdown_command(pdict, url, for_info=True)
    result = run_subprocess(command, cwd=work_dir)

    # 解析输出信息
    combined = "\n".join(filter(None, [result.get("stdout", ""), result.get("stderr", "")]))

    items = extract_page_items_from_text(combined)
    pages_source = "命令行解析"
    media_title = ""

    if not items or "番剧" in combined or "season" in url:
        api_items, api_title, api_source = fetch_page_items_from_bilibili_api(url, pdict)
        if api_items:
            items = api_items
            media_title = api_title
            pages_source = api_source

    result.update({
        "normalized_url": url,
        "pages": items,
        "pages_source": pages_source,
        "media_title": media_title,
        "qualities": extract_qualities(combined),
        "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    return result

@router.post("/url-download")
def api_url_download(payload: UrlDownloadPayload):
    url = normalize_video_target(payload.url)
    if not url:
         return {"error": "Invalid URL"}

    command, work_dir, _ = build_bbdown_command(payload.model_dump(), url, for_info=False)
    result = run_subprocess(command, cwd=work_dir)
    result["normalized_url"] = url
    result["finished_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return result

@router.post("/url-batch")
def api_url_batch(payload: UrlBatchPayload):
    return run_batch_downloads(payload.model_dump())
