from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path


INVALID_FILENAME_CHARS = '<>:"/\\|?*'
INVALID_FILENAME_REGEX = re.compile(f"[{re.escape(INVALID_FILENAME_CHARS)}]")
BILIBILI_CACHE_PREFIX = b"000000000"
BILIBILI_CACHE_PREFIX_LEN = len(BILIBILI_CACHE_PREFIX)
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}
TEXT_ENCODINGS = ("utf-8-sig", "utf-8", "gb18030")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="将 bilibili 缓存目录中的 m4s 音视频合并为 MP4。",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "示例:\n"
            "  py -3 scripts\\bilibili_cache_to_mp4.py "
            "\"C:\\Users\\曹乐\\Videos\\bilibili\\1221923803\"\n"
            "  py -3 scripts\\bilibili_cache_to_mp4.py "
            "\"C:\\Users\\曹乐\\Videos\\bilibili\" --output \"D:\\Videos\\导出\"\n"
            "  py -3 scripts\\bilibili_cache_to_mp4.py --dry-run"
        ),
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        default=r"C:\Users\曹乐\Videos\bilibili",
        help="单个 bilibili 缓存目录，或 bilibili 缓存根目录。",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="输出文件或输出目录；不填时单个目录输出到原目录，批量时输出到 input_path\\mp4。",
    )
    parser.add_argument(
        "--ffmpeg",
        default="ffmpeg",
        help="ffmpeg 可执行文件路径，默认直接使用 PATH 中的 ffmpeg。",
    )
    parser.add_argument(
        "--ffprobe",
        help="ffprobe 可执行文件路径；不填时会优先从 ffmpeg 同目录推断。",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="覆盖已存在的输出文件。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印将要执行的操作，不真正调用 ffmpeg。",
    )
    return parser.parse_args()


def resolve_executable(command: str, display_name: str) -> str:
    found = shutil.which(command)
    if found:
        return found
    candidate = Path(command).expanduser()
    if candidate.exists():
        return str(candidate)
    raise FileNotFoundError(f"未找到 {display_name}: {command}")


def guess_ffprobe(ffmpeg: str, explicit: str | None) -> str:
    if explicit:
        return resolve_executable(explicit, "ffprobe")
    ffmpeg_path = Path(ffmpeg)
    if ffmpeg_path.exists():
        sibling = ffmpeg_path.with_name("ffprobe" + ffmpeg_path.suffix)
        if sibling.exists():
            return str(sibling)
    return shutil.which("ffprobe") or ""


def find_cache_dirs(input_path: Path) -> list[Path]:
    if not input_path.exists():
        raise FileNotFoundError(f"路径不存在: {input_path}")
    if not input_path.is_dir():
        raise NotADirectoryError(f"请输入目录路径: {input_path}")
    if any(input_path.glob("*.m4s")):
        return [input_path]
    return sorted(
        child for child in input_path.iterdir() if child.is_dir() and any(child.glob("*.m4s"))
    )


def read_json_with_fallback(path: Path) -> dict:
    for encoding in TEXT_ENCODINGS:
        try:
            return json.loads(path.read_text(encoding=encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return {}


def read_metadata(cache_dir: Path) -> dict:
    for name in ("videoInfo.json", ".videoInfo"):
        path = cache_dir / name
        if path.exists():
            data = read_json_with_fallback(path)
            if isinstance(data, dict):
                return data
    return {}


def sanitize_filename(name: str, fallback: str) -> str:
    cleaned = (name or "").strip()
    cleaned = INVALID_FILENAME_REGEX.sub("_", cleaned)
    cleaned = " ".join(cleaned.split()).rstrip(". ")
    if not cleaned:
        cleaned = fallback
    if cleaned.upper() in WINDOWS_RESERVED_NAMES:
        cleaned = f"_{cleaned}"
    return cleaned


def build_output_stem(cache_dir: Path, metadata: dict) -> str:
    title = str(metadata.get("title") or metadata.get("groupTitle") or "").strip()
    bvid = str(metadata.get("bvid") or "").strip()
    page = metadata.get("p")
    if title:
        stem = title
    elif bvid:
        stem = bvid
    else:
        stem = cache_dir.name
    if page and str(page) != "1" and f"P{page}" not in stem:
        stem = f"{stem}-P{page}"
    return sanitize_filename(stem, cache_dir.name)


def has_bilibili_cache_prefix(media_path: Path) -> bool:
    with media_path.open("rb") as handle:
        prefix = handle.read(BILIBILI_CACHE_PREFIX_LEN)
    return prefix == BILIBILI_CACHE_PREFIX


def strip_bilibili_cache_prefix(source_path: Path, target_path: Path) -> Path:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with source_path.open("rb") as source_handle, target_path.open("wb") as target_handle:
        source_handle.seek(BILIBILI_CACHE_PREFIX_LEN)
        shutil.copyfileobj(source_handle, target_handle, length=1024 * 1024)
    return target_path


def prepare_media_for_ffmpeg(media_path: Path, temp_dir: Path) -> tuple[Path, bool]:
    if not has_bilibili_cache_prefix(media_path):
        return media_path, False
    normalized_path = temp_dir / media_path.name
    return strip_bilibili_cache_prefix(media_path, normalized_path), True


def probe_stream_types(ffprobe: str, media_path: Path) -> set[str]:
    if not ffprobe:
        return set()
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "stream=codec_type", "-of", "json", str(media_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        check=False,
    )
    if result.returncode != 0:
        return set()
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return set()
    streams = payload.get("streams") or []
    return {stream.get("codec_type") for stream in streams if stream.get("codec_type")}


def pick_stream_files(cache_dir: Path, ffprobe: str) -> tuple[Path, Path]:
    m4s_files = sorted(cache_dir.glob("*.m4s"), key=lambda item: item.stat().st_size, reverse=True)
    if len(m4s_files) < 2:
        raise ValueError(f"目录中至少需要 2 个 m4s 文件: {cache_dir}")

    video_candidates: list[Path] = []
    audio_candidates: list[Path] = []

    for media_path in m4s_files:
        stream_types = probe_stream_types(ffprobe, media_path)
        if "video" in stream_types:
            video_candidates.append(media_path)
        if "audio" in stream_types:
            audio_candidates.append(media_path)

    if not video_candidates:
        for candidate in m4s_files:
            if candidate not in audio_candidates:
                video_candidates.append(candidate)
                break

    if not audio_candidates:
        for candidate in reversed(m4s_files):
            if candidate not in video_candidates:
                audio_candidates.append(candidate)
                break

    if not video_candidates or not audio_candidates:
        raise ValueError(f"无法识别音视频文件: {cache_dir}")

    video_file = max(video_candidates, key=lambda item: item.stat().st_size)
    audio_file = max(audio_candidates, key=lambda item: item.stat().st_size)

    if video_file == audio_file:
        raise ValueError(f"音视频识别结果冲突: {cache_dir}")

    return video_file, audio_file


def ensure_unique_path(path: Path, used_paths: set[str]) -> Path:
    candidate = path
    index = 1
    while str(candidate).lower() in used_paths:
        candidate = candidate.with_name(f"{path.stem}_{index}{path.suffix}")
        index += 1
    used_paths.add(str(candidate).lower())
    return candidate


def build_output_path(
    cache_dir: Path,
    input_path: Path,
    output: str | None,
    metadata: dict,
    multiple: bool,
    used_paths: set[str],
) -> Path:
    stem = build_output_stem(cache_dir, metadata)

    if output:
        output_path = Path(output).expanduser()
        if output_path.suffix.lower() == ".mp4":
            if multiple:
                raise ValueError("批量转换时 --output 只能指定目录，不能指定单个 mp4 文件。")
            return ensure_unique_path(output_path, used_paths)
        base_path = output_path / f"{stem}.mp4"
        return ensure_unique_path(base_path, used_paths)

    if multiple:
        base_path = input_path / "mp4" / f"{stem}.mp4"
        return ensure_unique_path(base_path, used_paths)

    base_path = cache_dir / f"{stem}.mp4"
    return ensure_unique_path(base_path, used_paths)


def format_command(command: list[str]) -> str:
    return subprocess.list2cmdline(command)


def run_ffmpeg(
    ffmpeg: str,
    video_file: Path,
    audio_file: Path,
    output_file: Path,
    force: bool,
    dry_run: bool,
) -> bool:
    temp_base_dir = output_file.parent if output_file.parent.exists() else Path.cwd() / ".tmp"
    temp_base_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = temp_base_dir / f"bilibili-cache-{uuid.uuid4().hex}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        prepared_video_file, stripped_video_prefix = prepare_media_for_ffmpeg(video_file, temp_dir)
        prepared_audio_file, stripped_audio_prefix = prepare_media_for_ffmpeg(audio_file, temp_dir)

        command = [
            ffmpeg,
            "-y" if force else "-n",
            "-i",
            str(prepared_video_file),
            "-i",
            str(prepared_audio_file),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c",
            "copy",
            str(output_file),
        ]

        print(f"  视频: {video_file.name}")
        print(f"  音频: {audio_file.name}")
        print(f"  输出: {output_file}")
        if stripped_video_prefix or stripped_audio_prefix:
            print("  预处理: 已自动去除 bilibili 缓存的 9 字节前缀")
        print(f"  命令: {format_command(command)}")

        if dry_run:
            return True

        output_file.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(command, check=False)
        return result.returncode == 0
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> int:
    args = parse_args()

    try:
        ffmpeg = resolve_executable(args.ffmpeg, "ffmpeg")
        ffprobe = guess_ffprobe(ffmpeg, args.ffprobe)
        cache_dirs = find_cache_dirs(Path(args.input_path).expanduser())
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    if not cache_dirs:
        print(f"[ERROR] 未找到 bilibili 缓存目录: {args.input_path}")
        return 1

    if not ffprobe:
        print("[WARN] 未找到 ffprobe，将按文件大小兜底识别音视频。")

    multiple = len(cache_dirs) > 1
    used_paths: set[str] = set()
    failed_dirs: list[Path] = []

    for cache_dir in cache_dirs:
        print(f"[INFO] 处理目录: {cache_dir}")
        try:
            metadata = read_metadata(cache_dir)
            output_path = build_output_path(
                cache_dir=cache_dir,
                input_path=Path(args.input_path).expanduser(),
                output=args.output,
                metadata=metadata,
                multiple=multiple,
                used_paths=used_paths,
            )
            if output_path.exists() and not args.force:
                print(f"  跳过: 输出已存在，使用 --force 可覆盖 -> {output_path}")
                continue

            video_file, audio_file = pick_stream_files(cache_dir, ffprobe)
            ok = run_ffmpeg(
                ffmpeg=ffmpeg,
                video_file=video_file,
                audio_file=audio_file,
                output_file=output_path,
                force=args.force,
                dry_run=args.dry_run,
            )
            if ok:
                print("  结果: 成功")
            else:
                print("  结果: 失败")
                failed_dirs.append(cache_dir)
        except ValueError as exc:
            print(f"  错误: {exc}")
            failed_dirs.append(cache_dir)

    if failed_dirs:
        print("\n以下目录转换失败:")
        for failed_dir in failed_dirs:
            print(f"  - {failed_dir}")
        return 1

    print("\n全部处理完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
