import os
import shutil
import functools
import re
from pathlib import Path

from backend.constants import SYSTEM_DOTNET_ROOT

def apply_direct_connection_env(env: dict[str, str]) -> None:
    # Use direct connection by stripping proxies
    for key in list(env.keys()):
        if key.lower().endswith("proxy"):
            env.pop(key, None)

def build_process_env(prefer_system_dotnet: bool = False, disable_proxy: bool = False) -> dict[str, str]:
    env = os.environ.copy()
    if prefer_system_dotnet and SYSTEM_DOTNET_ROOT.exists():
        current_path = env.get("PATH", "")
        if str(SYSTEM_DOTNET_ROOT) not in current_path:
            env["PATH"] = f"{SYSTEM_DOTNET_ROOT}{os.pathsep}{current_path}"

    if disable_proxy:
        apply_direct_connection_env(env)

    return env

def resolve_executable_path(command: str) -> Path | None:
    if not command:
        return None
    direct_path = Path(command)
    if direct_path.is_file():
        return direct_path.resolve()
    found = shutil.which(command)
    return Path(found).resolve() if found else None

@functools.lru_cache(maxsize=None)
def get_scoop_roots() -> tuple[Path, ...]:
    roots: list[Path] = []
    for env_name in ("SCOOP", "SCOOP_GLOBAL"):
        value = os.environ.get(env_name, "").strip()
        if value:
            candidate = Path(value)
            if candidate.is_dir():
                roots.append(candidate.resolve())

    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        default_scoop = Path(user_profile) / "scoop"
        if default_scoop.is_dir() and default_scoop not in roots:
            roots.append(default_scoop.resolve())

    program_data = os.environ.get("ProgramData")
    if program_data:
        global_scoop = Path(program_data) / "scoop"
        if global_scoop.is_dir() and global_scoop not in roots:
            roots.append(global_scoop.resolve())

    return tuple(roots)

def iter_tool_candidates(tool_key: str) -> list[Path]:
    candidates: list[Path] = []
    win_ext = ".exe" if os.name == "nt" else ""
    basename = tool_key.lower()

    app_root = Path(__file__).resolve().parent.parent
    local_bin = app_root / "bin" / f"{basename}{win_ext}"
    if local_bin.is_file():
        candidates.append(local_bin)

    local_root_bin = app_root / f"{basename}{win_ext}"
    if local_root_bin.is_file():
        candidates.append(local_root_bin)

    scoop_apps = {
        "bbdown": ["bbdown"],
        "ffmpeg": ["ffmpeg"],
        "ffprobe": ["ffmpeg"],
        "mp4box": ["gpac"],
        "aria2c": ["aria2"],
    }

    app_names = scoop_apps.get(basename, [])
    for root in get_scoop_roots():
        for app_name in app_names:
            app_dir = root / "apps" / app_name / "current"
            if app_dir.is_dir():
                if basename in ("ffmpeg", "ffprobe"):
                    candidate = app_dir / "bin" / f"{basename}{win_ext}"
                else:
                    candidate = app_dir / f"{basename}{win_ext}"

                if candidate.is_file():
                    candidates.append(candidate)

    # Common system paths for windows
    if os.name == "nt":
        if basename == "bbdown":
            dotnet_tools = Path(os.path.expandvars(r"%USERPROFILE%\.dotnet\tools\bbdown.exe"))
            if dotnet_tools.is_file():
                candidates.append(dotnet_tools)
        elif basename in ("ffmpeg", "ffprobe"):
            for drive in ("C:", "D:", "E:"):
                for p in (rf"{drive}\ffmpeg\bin\{basename}.exe", rf"{drive}\Program Files\ffmpeg\bin\{basename}.exe"):
                    cand = Path(p)
                    if cand.is_file():
                        candidates.append(cand)

    return candidates

def probe_tool_version(tool_key: str, executable: Path) -> str:
    import subprocess
    cmd = [str(executable), "--version"]
    if tool_key == "mp4box":
        cmd = [str(executable), "-version"]

    try:
        env = build_process_env(prefer_system_dotnet=(tool_key == "bbdown"))
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=3, env=env)
        output = result.stdout.strip() or result.stderr.strip()
        if not output:
            return ""

        first_line = output.splitlines()[0][:100]
        if tool_key == "bbdown":
            match = re.search(r"BBDown\s+v?([\d\.]+)", first_line, re.IGNORECASE)
            return match.group(1) if match else first_line
        if tool_key in ("ffmpeg", "ffprobe"):
            match = re.search(r"version\s+([^\s]+)", first_line)
            return match.group(1) if match else first_line
        if tool_key == "aria2c":
            match = re.search(r"aria2\s+version\s+([\d\.]+)", first_line)
            return match.group(1) if match else first_line
        if tool_key == "mp4box":
            match = re.search(r"MP4Box\s+-\s+GPAC\s+version\s+([\d\.]+)", first_line)
            return match.group(1) if match else first_line

        return first_line
    except Exception:
        return ""

def detect_single_tool(tool_key: str, configured_path: str = "") -> dict[str, object]:
    from backend.constants import TOOL_LABELS

    result = {
        "key": tool_key,
        "label": TOOL_LABELS.get(tool_key, tool_key),
        "found": False,
        "path": "",
        "source": "",
        "version": "",
        "searched": []
    }

    searched = []

    if configured_path:
        resolved = resolve_executable_path(configured_path)
        if resolved:
            result.update({
                "found": True,
                "path": str(resolved),
                "source": "configured",
                "version": probe_tool_version(tool_key, resolved)
            })
            return result
        searched.append(configured_path)

    for cand in iter_tool_candidates(tool_key):
        searched.append(str(cand))
        if cand.is_file():
            result.update({
                "found": True,
                "path": str(cand),
                "source": "common_paths",
                "version": probe_tool_version(tool_key, cand)
            })
            return result

    sys_path = resolve_executable_path(tool_key)
    if sys_path:
        result.update({
            "found": True,
            "path": str(sys_path),
            "source": "system_path",
            "version": probe_tool_version(tool_key, sys_path)
        })
        return result

    searched.append(f"system_path: {tool_key}")
    result["searched"] = searched

    return result

def detect_tool_paths(payload: dict) -> dict[str, object]:
    from backend.constants import TOOL_FIELD_BINDINGS
    tools_info = {}
    fill_fields = {}

    for tool_key, fields in TOOL_FIELD_BINDINGS.items():
        if isinstance(fields, str):
            fields = [fields]

        configured = ""
        for f in fields:
            val = payload.get(f, "").strip()
            if val:
                configured = val
                break

        info = detect_single_tool(tool_key, configured)
        tools_info[tool_key] = info

        if info["found"] and info["path"]:
            for f in fields:
                if not payload.get(f, "").strip():
                    fill_fields[f] = info["path"]

    all_found = all(t["found"] for t in tools_info.values())

    return {
        "ok": True,
        "tools": tools_info,
        "fields": fill_fields,
        "message": "所有工具均已就绪。" if all_found else "部分工具未找到，可能会影响相应功能。"
    }
