import json
import re
import shlex
import subprocess
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request
from datetime import datetime

from backend.constants import (
    BILIBILI_ID_PATTERN,
    DEFAULT_BBDOWN,
    PAGE_LINE_PATTERNS,
    TRAILING_URL_PUNCTUATION,
    URL_CANDIDATE_PATTERN,
    VALID_QUALITIES,
)
from backend.tools import build_process_env

def extract_qualities(text: str) -> list[str]:
    return [q for q in VALID_QUALITIES if q in text]

def format_duration_text(seconds: int | float | str | None) -> str:
    try:
        total_seconds = int(float(seconds or 0))
    except (TypeError, ValueError):
        return ""
    if total_seconds <= 0:
        return ""
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def build_http_json_request(url: str, cookie_text: str = "") -> dict[str, object]:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.bilibili.com/",
    }
    if cookie_text:
        headers["Cookie"] = cookie_text
    request = urllib_request.Request(url, headers=headers)
    opener = urllib_request.build_opener(urllib_request.ProxyHandler({}))
    with opener.open(request, timeout=8) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload if isinstance(payload, dict) else {}

def extract_bilibili_identifier(raw_target: str) -> tuple[str, str]:
    match = BILIBILI_ID_PATTERN.search(raw_target)
    if not match:
        return "", ""
    value = match.group(1)
    lower_value = value.lower()
    if lower_value.startswith("bv"):
        return "bv", "BV" + value[2:]
    if lower_value.startswith("av"):
        return "av", lower_value[2:]
    if lower_value.startswith("ep"):
        return "ep", lower_value[2:]
    if lower_value.startswith("ss"):
        return "ss", lower_value[2:]
    return "", ""

def get_bbdown_data_candidates(bbdown_path: str) -> list[Path]:
    candidates = []
    base_name = "BBDown.data"
    candidates.append(Path.cwd() / base_name)
    if bbdown_path:
        bbdown_file = Path(bbdown_path)
        if bbdown_file.is_file():
            candidates.append(bbdown_file.parent / base_name)

    app_root = Path(__file__).resolve().parent.parent
    candidates.append(app_root / "bin" / base_name)
    candidates.append(app_root / base_name)

    import os
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        candidates.append(Path(user_profile) / ".bbdown" / base_name)

    return candidates

def read_cookie_data_file(path: Path) -> tuple[str, dict[str, str]]:
    try:
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return "", {}

        cookie_text = ""
        cookies = {}
        for line in content.splitlines():
            line = line.strip()
            if line and "SESSDATA=" in line:
                cookie_text = line
                cookies = parse_cookie_string(line)
                break

        if not cookie_text:
            cookie_text = content.splitlines()[0].strip()
            cookies = parse_cookie_string(cookie_text)

        return cookie_text, cookies
    except Exception:
        return "", {}

def parse_cookie_string(cookie_text: str) -> dict[str, str]:
    cookies = {}
    for part in cookie_text.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            cookies[k.strip()] = v.strip()
    return cookies

def get_request_cookie_text(payload: dict) -> str:
    explicit_cookie = str(payload.get("cookie", "")).strip()
    if explicit_cookie:
        return explicit_cookie

    bbdown_path = str(payload.get("bbdown_path", "")).strip() or DEFAULT_BBDOWN
    for data_path in get_bbdown_data_candidates(bbdown_path):
        if not data_path.exists():
            continue
        cookie_text, cookies = read_cookie_data_file(data_path)
        if cookies:
            return cookie_text
    return ""

def fetch_page_items_from_bilibili_api(target: str, payload: dict) -> tuple[list[dict[str, object]], str, str]:
    kind, identifier = extract_bilibili_identifier(target)
    if not kind:
        return [], "", ""

    cookie_text = get_request_cookie_text(payload)
    try:
        if kind == "bv":
            api_payload = build_http_json_request(
                f"https://api.bilibili.com/x/web-interface/view?bvid={identifier}",
                cookie_text=cookie_text,
            )
            data = api_payload.get("data")
            if not isinstance(data, dict):
                return [], "", ""
            pages = data.get("pages")
            if not isinstance(pages, list):
                return [], "", ""
            items: list[dict[str, object]] = []
            for page in pages:
                if not isinstance(page, dict):
                    continue
                index = int(page.get("page") or len(items) + 1)
                title = str(page.get("part") or f"P{index}")
                duration = format_duration_text(page.get("duration"))
                items.append({
                    "index": index,
                    "title": title,
                    "subtitle": duration,
                    "label": f"P{index} · {title}" if title else f"P{index}",
                })
            return items, str(data.get("title") or ""), "video-api"

        if kind == "av":
            api_payload = build_http_json_request(
                f"https://api.bilibili.com/x/web-interface/view?aid={identifier}",
                cookie_text=cookie_text,
            )
            data = api_payload.get("data")
            if not isinstance(data, dict):
                return [], "", ""
            pages = data.get("pages")
            if not isinstance(pages, list):
                return [], "", ""
            items = []
            for page in pages:
                if not isinstance(page, dict):
                    continue
                index = int(page.get("page") or len(items) + 1)
                title = str(page.get("part") or f"P{index}")
                duration = format_duration_text(page.get("duration"))
                items.append({
                    "index": index,
                    "title": title,
                    "subtitle": duration,
                    "label": f"P{index} · {title}" if title else f"P{index}",
                })
            return items, str(data.get("title") or ""), "video-api"

        if kind in {"ep", "ss"}:
            query_key = "ep_id" if kind == "ep" else "season_id"
            api_payload = build_http_json_request(
                f"https://api.bilibili.com/pgc/view/web/season?{query_key}={identifier}",
                cookie_text=cookie_text,
            )
            data = api_payload.get("result") or api_payload.get("data")
            if not isinstance(data, dict):
                return [], "", ""
            items: list[dict[str, object]] = []

            def append_episode_block(episodes: object, block_title: str = "") -> None:
                if not isinstance(episodes, list):
                    return
                for episode in episodes:
                    if not isinstance(episode, dict):
                        continue
                    index = len(items) + 1
                    short_title = str(episode.get("title") or index)
                    long_title = str(episode.get("long_title") or "").strip()
                    badge = str(episode.get("badge") or "").strip()
                    title_parts = [part for part in [short_title, long_title] if part]
                    title = " · ".join(title_parts)
                    subtitle_parts = [part for part in [block_title, badge] if part]
                    items.append({
                        "index": index,
                        "title": title,
                        "subtitle": " · ".join(subtitle_parts),
                        "label": f"{index}. {title}" if title else f"{index}.",
                    })

            append_episode_block(data.get("episodes"))
            sections = data.get("section")
            if isinstance(sections, list):
                for section in sections:
                    if not isinstance(section, dict):
                        continue
                    append_episode_block(section.get("episodes"), str(section.get("title") or "").strip())
            return items, str(data.get("title") or ""), "season-api"
    except (OSError, urllib_error.URLError, ValueError, json.JSONDecodeError):
        return [], "", ""

    return [], "", ""

def extract_page_items_from_text(text: str) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    seen: set[int] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or len(line) < 2:
            continue
        if any(token in line.lower() for token in ("http://", "https://", "aid", "bvid", "cid", "清晰度", "音频", "视频")):
            continue
        for pattern in PAGE_LINE_PATTERNS:
            match = pattern.match(line)
            if not match:
                continue
            index = int(match.group("index"))
            if index <= 0 or index > 999 or index in seen:
                continue
            title = match.group("title").strip()
            if not title:
                continue
            seen.add(index)
            items.append({
                "index": index,
                "title": title,
                "subtitle": "",
                "label": f"{index}. {title}",
            })
            break
    return items

def ensure_output_dir(output: str) -> Path:
    output_dir = Path(output).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def strip_trailing_url_punctuation(value: str) -> str:
    return value.rstrip(TRAILING_URL_PUNCTUATION)

def normalize_video_target(raw_text: str) -> str:
    text = raw_text.strip()
    if not text:
        return ""

    url_match = URL_CANDIDATE_PATTERN.search(text)
    if url_match:
        return strip_trailing_url_punctuation(url_match.group(0))

    id_match = BILIBILI_ID_PATTERN.search(text)
    if not id_match:
        return text

    value = id_match.group(1)
    lower_value = value.lower()
    if lower_value.startswith("bv"):
        return "BV" + value[2:]
    if lower_value.startswith("av"):
        return "av" + value[2:]
    return lower_value

def normalize_page_spec(raw_text: str) -> str:
    value = raw_text.strip()
    if not value:
        return ""
    upper_value = value.upper()
    if upper_value in {"ALL", "LAST"}:
        return upper_value
    return re.sub(r"\s+", "", value)

def extend_with_extra_args(command: list[str], extra_args: str) -> None:
    if not extra_args.strip():
        return
    try:
        command.extend(shlex.split(extra_args, posix=False))
    except ValueError:
        command.extend(extra_args.split())

def extend_bbdown_options(command: list[str], payload: dict, for_info: bool = False) -> dict[str, object]:
    page_spec = normalize_page_spec(str(payload.get("page_spec", "")))
    show_all_pages = bool(payload.get("show_all_pages"))
    api_mode = str(payload.get("api_mode", "")).strip()
    encoding_priority = str(payload.get("encoding_priority", "")).strip()
    language = str(payload.get("language", "")).strip()
    user_agent = str(payload.get("user_agent", "")).strip()
    cookie = str(payload.get("cookie", "")).strip()
    access_token = str(payload.get("access_token", "")).strip()
    download_mode = str(payload.get("download_mode", "")).strip()
    download_danmaku = bool(payload.get("download_danmaku"))
    skip_subtitle = bool(payload.get("skip_subtitle"))
    skip_cover = bool(payload.get("skip_cover"))
    use_aria2c = bool(payload.get("use_aria2c"))
    use_mp4box = bool(payload.get("use_mp4box"))
    skip_mux = bool(payload.get("skip_mux"))
    hide_streams = bool(payload.get("hide_streams"))
    debug_mode = bool(payload.get("debug_mode"))
    download_ai_subtitle = bool(payload.get("download_ai_subtitle"))
    video_ascending = bool(payload.get("video_ascending"))
    audio_ascending = bool(payload.get("audio_ascending"))
    allow_pcdn = bool(payload.get("allow_pcdn"))
    save_archives_to_file = bool(payload.get("save_archives_to_file"))
    ffmpeg_path = str(payload.get("ffmpeg_path", "")).strip()
    mp4box_path = str(payload.get("mp4box_path", "")).strip()
    aria2c_path = str(payload.get("aria2c_path", "")).strip()
    aria2c_args = str(payload.get("aria2c_args", "")).strip()
    delay_per_page = str(payload.get("delay_per_page", "")).strip()
    file_pattern = str(payload.get("file_pattern", "")).strip()
    multi_file_pattern = str(payload.get("multi_file_pattern", "")).strip()
    work_dir_override = str(payload.get("work_dir_override", "")).strip()
    upos_host = str(payload.get("upos_host", "")).strip()
    host = str(payload.get("host", "")).strip()
    ep_host = str(payload.get("ep_host", "")).strip()
    area = str(payload.get("area", "")).strip()
    config_file = str(payload.get("config_file", "")).strip()
    extra_args = str(payload.get("extra_args", "")).strip()

    if page_spec:
        command.extend(["-p", page_spec])
    if show_all_pages:
        command.append("--show-all")

    if api_mode == "tv":
        command.append("--use-tv-api")
    elif api_mode == "app":
        command.append("--use-app-api")
    elif api_mode == "intl":
        command.append("--use-intl-api")

    if encoding_priority:
        command.extend(["--encoding-priority", encoding_priority])
    if language:
        command.extend(["--language", language])
    if user_agent:
        command.extend(["--user-agent", user_agent])
    if cookie:
        command.extend(["--cookie", cookie])
    if access_token:
        command.extend(["--access-token", access_token])

    if hide_streams:
        command.append("--hide-streams")
    if debug_mode:
        command.append("--debug")
    if use_mp4box:
        command.append("--use-mp4box")
    if ffmpeg_path:
        command.extend(["--ffmpeg-path", ffmpeg_path])
    if mp4box_path:
        command.extend(["--mp4box-path", mp4box_path])
    if file_pattern:
        command.extend(["--file-pattern", file_pattern])
    if multi_file_pattern:
        command.extend(["--multi-file-pattern", multi_file_pattern])
    if work_dir_override:
        command.extend(["--work-dir", work_dir_override])
    if upos_host:
        command.extend(["--upos-host", upos_host])
    if host:
        command.extend(["--host", host])
    if ep_host:
        command.extend(["--ep-host", ep_host])
    if area:
        command.extend(["--area", area])
    if config_file:
        command.extend(["--config-file", config_file])
    if delay_per_page:
        command.extend(["--delay-per-page", delay_per_page])
    if save_archives_to_file:
        command.append("--save-archives-to-file")

    if not for_info:
        if download_mode:
            command.append(f"--{download_mode}")
        if download_danmaku:
            command.append("--download-danmaku")
        if skip_subtitle:
            command.append("--skip-subtitle")
        if skip_cover:
            command.append("--skip-cover")
        if use_aria2c:
            command.append("--use-aria2c")
        if aria2c_path:
            command.extend(["--aria2c-path", aria2c_path])
        if aria2c_args:
            command.extend(["--aria2c-args", f'"{aria2c_args}"'])
        if skip_mux:
            command.append("--skip-mux")
        if download_ai_subtitle:
            command.append("--ai-subtitle")
        if video_ascending:
            command.append("--video-ascending")
        if audio_ascending:
            command.append("--audio-ascending")
        if allow_pcdn:
            command.append("--allow-pcdn")

    extend_with_extra_args(command, extra_args)

    return {"command": command, "work_dir": Path.cwd()}

def run_subprocess(command: list[str], cwd: Path | None = None) -> dict[str, object]:
    command_str = " ".join(command)
    try:
        env = build_process_env(prefer_system_dotnet=True)
        process = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        return {
            "command": command_str,
            "returncode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
        }
    except FileNotFoundError:
        return {
            "command": command_str,
            "returncode": -1,
            "stdout": "",
            "stderr": "未找到执行文件，请检查路径是否正确配置。",
        }
    except Exception as e:
        return {
            "command": command_str,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
        }

def build_bbdown_command(payload: dict, url: str, for_info: bool = False) -> tuple[list[str], Path, dict[str, object]]:
    bbdown_path = str(payload.get("bbdown_path", "")).strip() or DEFAULT_BBDOWN
    command = [bbdown_path]
    output = str(payload.get("output", "")).strip()
    work_dir = ensure_output_dir(output) if output else Path.cwd()

    if for_info:
        command.append("--info")
    else:
        quality = str(payload.get("quality", "")).strip()
        if quality:
            command.extend(["--dfn-priority", quality])

    opts = extend_bbdown_options(command, payload, for_info=for_info)
    if "work_dir" in opts:
        pass
    command.append(url)
    return command, work_dir, opts

def split_batch_targets(raw_text: str) -> list[str]:
    targets = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        norm = normalize_video_target(line)
        if norm:
            targets.append(norm)
    return targets

def run_batch_downloads(payload: dict) -> dict[str, object]:
    raw_text = str(payload.get("urls_text", ""))
    targets = split_batch_targets(raw_text)
    if not targets:
        return {
            "command": "batch",
            "returncode": -1,
            "stdout": "",
            "stderr": "未提供有效的下载链接。",
            "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    continue_on_error = bool(payload.get("batch_continue_on_error"))
    combined_stdout = []
    combined_stderr = []
    final_returncode = 0

    for index, target in enumerate(targets):
        command, work_dir, _ = build_bbdown_command(payload, target, for_info=False)
        result = run_subprocess(command, cwd=work_dir)
        header = f"\n=== [{index + 1}/{len(targets)}] {target} ===\n"
        combined_stdout.append(header + str(result.get("stdout", "")))

        err = str(result.get("stderr", "")).strip()
        if err:
            combined_stderr.append(header + err)

        if result.get("returncode", 0) != 0:
            final_returncode = int(result.get("returncode", -1))
            if not continue_on_error:
                combined_stderr.append("\n[中止] 因发生错误且未开启“继续后续任务”，批量队列已停止。")
                break

    return {
        "command": "批量下载",
        "returncode": final_returncode,
        "stdout": "\n".join(combined_stdout).strip(),
        "stderr": "\n".join(combined_stderr).strip(),
        "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

def format_expire_time(raw_expire: str) -> str:
    try:
        ts = float(raw_expire)
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return raw_expire

def fetch_bilibili_nav_info(cookie_text: str) -> dict[str, object]:
    payload = build_http_json_request("https://api.bilibili.com/x/web-interface/nav", cookie_text=cookie_text)
    data = payload.get("data")
    if isinstance(data, dict):
        return {
            "isLogin": bool(data.get("isLogin")),
            "uname": str(data.get("uname", "")),
            "mid": str(data.get("mid", "")),
        }
    return {}

def get_bbdown_login_status(bbdown_path: str) -> dict[str, object]:
    result = {
        "logged_in": False,
        "account_name": "",
        "uid": "",
        "login_type": "",
        "expires_at": "",
        "message": "未找到登录数据。",
    }

    for data_path in get_bbdown_data_candidates(bbdown_path):
        if not data_path.exists():
            continue
        cookie_text, cookies = read_cookie_data_file(data_path)
        if not cookies:
            continue

        access_token = cookies.get("access_token")
        if access_token:
            result.update({
                "logged_in": True,
                "login_type": "TV/APP",
                "message": "已通过 TV 或 APP 接口登录。"
            })
            return result

        sessdata = cookies.get("SESSDATA")
        if sessdata:
            nav_info = fetch_bilibili_nav_info(cookie_text)
            is_login = nav_info.get("isLogin")

            result.update({
                "logged_in": bool(is_login),
                "account_name": nav_info.get("uname", ""),
                "uid": nav_info.get("mid", ""),
                "login_type": "Web (SESSDATA)",
                "expires_at": format_expire_time(cookies.get("bili_ticket_expires", "")),
                "message": "获取账号信息成功。" if is_login else "Cookie 已过期或无效。"
            })
            return result

    return result

def clear_bbdown_login_data(bbdown_path: str) -> dict[str, object]:
    cleared = False
    for data_path in get_bbdown_data_candidates(bbdown_path):
        if data_path.exists():
            try:
                data_path.unlink()
                cleared = True
            except OSError:
                pass
    status = get_bbdown_login_status(bbdown_path)
    return {
        "ok": cleared,
        "message": "已清除找到的 BBDown 登录文件。" if cleared else "未找到可清除的登录文件。",
        "current_status": status,
    }

def start_bbdown_login_process(bbdown_path: str, mode: str) -> dict[str, object]:
    command = [bbdown_path or DEFAULT_BBDOWN, "login"]
    if mode == "tv":
        command.append("-tv")

    import subprocess
    import os
    import sys
    import shutil
    env = build_process_env(prefer_system_dotnet=True, disable_proxy=True)
    if os.name == "nt":
        subprocess.Popen(
            ["cmd.exe", "/c", "start", "BBDown 登录", *command],
            env=env
        )
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-a", "Terminal", *command], env=env)
    else:
        # Fallback Linux
        terminals = ["gnome-terminal", "xterm", "konsole", "alacritty"]
        for term in terminals:
            if shutil.which(term):
                subprocess.Popen([term, "-e", *command], env=env)
                break

    return {
        "ok": True,
        "message": f"已尝试唤起外部终端执行 BBDown {'TV ' if mode == 'tv' else 'Web '}登录。",
    }
