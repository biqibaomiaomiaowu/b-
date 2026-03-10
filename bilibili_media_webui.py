import argparse
import concurrent.futures
import json
import mimetypes
import os
import re
import shlex
import shutil
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from string import Template
from urllib import error as urllib_error
from urllib import request as urllib_request
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parent.parent
APP_ROOT = Path(__file__).resolve().parent
CACHE_CONVERTER_SCRIPT = Path(__file__).resolve().with_name("bilibili_cache_to_mp4.py")
FRONTEND_ROOT = APP_ROOT / "frontend"
FRONTEND_DIST_DIR = FRONTEND_ROOT / "dist"
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
    ".bilibili.com",
    ".b23.tv",
    ".hdslb.com",
    ".bilivideo.com",
    ".biliapi.com",
    ".biliapi.net",
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
    "1080P 高清",
    "720P 高清",
    "480P 清晰",
    "360P 流畅",
]
VALID_QUALITIES = [
    quality
    for quality in QUALITY_OPTIONS
    if quality != "自动（最高可用）"
]
TOOL_LABELS = {
    "bbdown": "BBDown",
    "ffmpeg": "ffmpeg",
    "ffprobe": "ffprobe",
    "aria2c": "aria2c",
    "mp4box": "MP4Box",
}
TOOL_FIELD_BINDINGS = {
    "bbdown": ["bbdown_path"],
    "ffmpeg": ["cache_ffmpeg", "ffmpeg_path"],
    "ffprobe": ["cache_ffprobe"],
    "aria2c": ["aria2c_path"],
    "mp4box": ["mp4box_path"],
}
PAGE_LINE_PATTERNS = [
    re.compile(r"^\s*\[(?P<index>\d{1,4})\]\s*(?P<title>.+?)\s*$"),
    re.compile(r"^\s*[Pp](?P<index>\d{1,4})\s*[:：.\-、\]]?\s*(?P<title>.+?)\s*$"),
    re.compile(r"^\s*(?:第\s*)?(?P<index>\d{1,4})\s*(?:[Pp]|话|集|期)\s*[:：.\-、]?\s*(?P<title>.+?)\s*$"),
    re.compile(r"^\s*(?P<index>\d{1,4})\s*[:：.\-、]\s*(?P<title>.+?)\s*$"),
]
HTML_TEMPLATE = Template(
    """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bilibili 下载 / 转换启动器</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #0b1020;
      --panel: #131a2d;
      --panel-border: #28304a;
      --text: #edf2ff;
      --muted: #9aa5c3;
      --accent: #5b8cff;
      --accent-hover: #7aa0ff;
      --ok: #22c55e;
      --warn: #f59e0b;
      --error: #ef4444;
      --input-bg: #0f1527;
    }
    @media (prefers-color-scheme: light) {
      :root {
        --bg: #f4f7fb;
        --panel: #ffffff;
        --panel-border: #d9e1f2;
        --text: #1f2937;
        --muted: #5b6475;
        --accent: #2563eb;
        --accent-hover: #1d4ed8;
        --ok: #15803d;
        --warn: #b45309;
        --error: #b91c1c;
        --input-bg: #f8fafc;
      }
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
    }
    .wrap {
      max-width: 1200px;
      margin: 0 auto;
      padding: 28px 18px 40px;
    }
    .hero {
      margin-bottom: 20px;
    }
    .hero h1 {
      margin: 0 0 8px;
      font-size: 30px;
    }
    .hero p {
      margin: 0;
      color: var(--muted);
      line-height: 1.65;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }
    @media (max-width: 920px) {
      .grid { grid-template-columns: 1fr; }
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
    }
    .card h2 {
      margin: 0 0 14px;
      font-size: 18px;
    }
    .field {
      margin-bottom: 14px;
    }
    .field label {
      display: block;
      margin-bottom: 6px;
      font-size: 14px;
      font-weight: 600;
    }
    .field small {
      display: block;
      margin-top: 6px;
      color: var(--muted);
      line-height: 1.55;
    }
    input[type="text"], select {
      width: 100%;
      padding: 11px 12px;
      border-radius: 12px;
      border: 1px solid var(--panel-border);
      background: var(--input-bg);
      color: var(--text);
      outline: none;
      font: inherit;
    }
    input[type="text"]:focus, select:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(91, 140, 255, 0.18);
    }
    .checkbox-row, .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }
    .checkbox-row {
      margin: 16px 0 2px;
    }
    .checkbox-row label {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      cursor: pointer;
    }
    .actions {
      margin-top: 16px;
    }
    button {
      border: 0;
      border-radius: 12px;
      padding: 11px 16px;
      font: inherit;
      cursor: pointer;
      transition: transform 0.06s ease, background 0.2s ease, opacity 0.2s ease;
    }
    button:hover { transform: translateY(-1px); }
    button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
    .primary {
      background: var(--accent);
      color: #fff;
    }
    .primary:hover { background: var(--accent-hover); }
    .secondary {
      background: transparent;
      border: 1px solid var(--panel-border);
      color: var(--text);
    }
    .status {
      margin-bottom: 12px;
      padding: 12px 14px;
      border-radius: 12px;
      background: rgba(91, 140, 255, 0.12);
      color: var(--text);
      line-height: 1.55;
    }
    .status.ok { background: rgba(34, 197, 94, 0.12); color: var(--ok); }
    .status.warn { background: rgba(245, 158, 11, 0.14); color: var(--warn); }
    .status.error { background: rgba(239, 68, 68, 0.14); color: var(--error); }
    .kv {
      display: grid;
      grid-template-columns: 100px 1fr;
      gap: 8px 12px;
      margin-bottom: 16px;
      font-size: 14px;
    }
    .kv div:nth-child(odd) {
      color: var(--muted);
    }
    pre {
      margin: 0;
      min-height: 360px;
      max-height: 780px;
      overflow: auto;
      padding: 14px;
      border-radius: 14px;
      background: #0a0f1d;
      color: #d5e3ff;
      border: 1px solid rgba(148, 163, 184, 0.18);
      white-space: pre-wrap;
      word-break: break-word;
      font-family: Consolas, "Cascadia Code", monospace;
      font-size: 13px;
      line-height: 1.55;
    }
    .footer {
      margin-top: 16px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.6;
    }
    .hidden {
      display: none;
    }
    .advanced-panel {
      margin-top: 14px;
      padding: 14px;
      border: 1px dashed var(--panel-border);
      border-radius: 14px;
      background: rgba(91, 140, 255, 0.06);
    }
    .advanced-panel h3 {
      margin: 0 0 12px;
      font-size: 15px;
    }
    .tool-status-list {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 10px;
      margin-top: 14px;
    }
    .tool-status-item {
      padding: 10px 12px;
      border-radius: 12px;
      border: 1px solid var(--panel-border);
      background: rgba(15, 21, 39, 0.28);
      font-size: 13px;
      line-height: 1.55;
    }
    .tool-status-item strong {
      display: block;
      margin-bottom: 4px;
      font-size: 14px;
    }
    .tool-status-item code {
      display: block;
      margin-top: 4px;
      word-break: break-all;
      color: var(--muted);
    }
    .page-picker-list {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 10px;
      margin-top: 14px;
      max-height: 320px;
      overflow: auto;
      padding-right: 4px;
    }
    .page-picker-item {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      padding: 10px 12px;
      border-radius: 12px;
      border: 1px solid var(--panel-border);
      background: rgba(15, 21, 39, 0.28);
    }
    .page-picker-item input {
      margin-top: 3px;
    }
    .page-picker-item strong,
    .page-picker-item small {
      display: block;
      line-height: 1.5;
    }
    .page-picker-item small {
      color: var(--muted);
    }
    .result-card {
      margin-top: 18px;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <h1>Bilibili 下载 / 转换启动器</h1>
      <p>一个本地网页界面，支持两种模式：<strong>缓存目录转 MP4</strong> 与 <strong>通过 B 站视频链接下载</strong>。链接下载模式会调用 <code>BBDown</code>，可查看画质信息并选择清晰度。</p>
    </div>

    <div class="grid">
      <section class="card">
        <h2>模式一：缓存目录转 MP4</h2>
        <form id="cache-form">
          <div class="field">
            <label for="cache_input_path">缓存目录</label>
            <input id="cache_input_path" type="text" value="$default_cache_path" required>
            <small>可填单个视频缓存目录，也可填整个 <code>bilibili</code> 根目录批量处理。</small>
          </div>
          <div class="field">
            <label for="cache_output">输出目录 / 输出文件</label>
            <input id="cache_output" type="text" placeholder="留空则按脚本默认规则输出">
          </div>
          <div class="field">
            <label for="cache_ffmpeg">ffmpeg 路径</label>
            <input id="cache_ffmpeg" type="text" value="ffmpeg">
          </div>
          <div class="field">
            <label for="cache_ffprobe">ffprobe 路径</label>
            <input id="cache_ffprobe" type="text" placeholder="留空则自动推断">
          </div>
          <div class="checkbox-row">
            <label><input id="cache_force" type="checkbox"> 强制覆盖已有输出</label>
            <label><input id="cache_dry_run" type="checkbox"> 仅预演，不真正执行</label>
          </div>
          <div class="actions">
            <button class="primary" id="cache_run_btn" type="submit">开始转换</button>
            <button class="secondary" id="cache_example_btn" type="button">填入示例</button>
          </div>
        </form>
      </section>

      <section class="card">
        <h2>模式二：视频链接下载</h2>
        <div class="advanced-panel" style="margin-bottom: 16px;">
          <h3>账号状态</h3>
          <div class="kv" style="margin-bottom: 12px;">
            <div>登录状态</div><div id="login_status_text">检查中...</div>
            <div>账号昵称</div><div id="login_account_name">-</div>
            <div>UID</div><div id="login_uid">-</div>
            <div>登录类型</div><div id="login_type">-</div>
            <div>过期时间</div><div id="login_expires_at">-</div>
          </div>
          <div id="login_status_message" class="status">正在获取登录状态...</div>
          <div class="actions">
            <button class="secondary" id="refresh_login_btn" type="button">刷新登录状态</button>
            <button class="secondary" id="login_web_btn" type="button">网页登录</button>
            <button class="secondary" id="login_tv_btn" type="button">TV 登录</button>
            <button class="secondary" id="clear_login_btn" type="button">退出登录</button>
          </div>
        </div>
        <div class="advanced-panel" style="margin-bottom: 16px;">
          <h3>工具路径自动发现</h3>
          <div id="tool_detect_message" class="status warn">启动后会自动补全空白工具路径；你也可以手动重新检测并覆盖。</div>
          <div class="actions">
            <button class="secondary" id="detect_tools_btn" type="button">自动检测工具路径</button>
          </div>
          <div id="tool_detect_list" class="tool-status-list"></div>
        </div>
        <form id="download-form">
          <div class="field">
            <label for="video_url">B 站视频链接</label>
            <input id="video_url" type="text" placeholder="例如：https://www.bilibili.com/video/BV..." required>
            <small>支持直接粘贴 <code>【标题】链接</code>、纯链接、<code>BV</code>/<code>av</code>/<code>ep</code>/<code>ss</code> 编号；页面会自动识别。</small>
          </div>
          <div class="field">
            <label for="download_output">下载目录</label>
            <input id="download_output" type="text" placeholder="留空则下载到当前仓库目录">
          </div>
          <div class="field">
            <label for="bbdown_path">BBDown 路径</label>
            <input id="bbdown_path" type="text" value="$default_bbdown">
            <small>根据 <code>BBDown</code> 仓库说明，可用 <code>-info</code> 查看信息，<code>-q</code> / <code>--dfn-priority</code> 选择清晰度。</small>
          </div>
          <div class="field">
            <label for="quality_select">清晰度</label>
            <select id="quality_select">$quality_options_html</select>
            <small>可先点“获取画质”查看链接支持的清晰度；下载时会优先使用你选择的清晰度。</small>
          </div>
          <div class="field">
            <label for="quality_custom">自定义清晰度文本</label>
            <input id="quality_custom" type="text" placeholder="例如：1080P 高码率">
            <small>如果下拉列表里没有你想要的项，可手动填写，优先级高于下拉选择。</small>
          </div>
          <div class="field">
            <label for="page_spec">分P / 剧集范围</label>
            <input id="page_spec" type="text" placeholder="留空=默认；全集填 ALL；也支持 1-5、1,3,7、LAST">
            <small>适用于多 P、合集、番剧、课程等。常见写法：<code>ALL</code>、<code>1-5</code>、<code>1,3,7</code>、<code>LAST</code>。</small>
          </div>
          <div class="checkbox-row">
            <label><input id="show_all_pages" type="checkbox"> 获取信息时显示全部分P / 剧集列表</label>
          </div>
          <div id="page_picker_panel" class="advanced-panel hidden">
            <h3>分P / 剧集可视化选择</h3>
            <div id="page_picker_hint" class="status warn">先点“获取画质”或“解析信息”，这里会显示可选分P / 剧集。</div>
            <div class="actions">
              <button class="secondary" id="page_picker_select_all_btn" type="button">全选</button>
              <button class="secondary" id="page_picker_clear_btn" type="button">清空</button>
              <button class="secondary" id="page_picker_invert_btn" type="button">反选</button>
              <button class="secondary" id="page_picker_refresh_btn" type="button">重新解析列表</button>
            </div>
            <div id="page_picker_list" class="page-picker-list"></div>
          </div>
          <div class="actions">
            <button class="secondary" id="toggle_advanced_btn" type="button">显示更多功能</button>
          </div>
          <div id="advanced_download_options" class="advanced-panel hidden">
            <h3>高级下载选项</h3>
            <div class="field">
              <label for="download_mode">下载模式</label>
              <select id="download_mode">
                <option value="">默认（正常下载）</option>
                <option value="video-only">仅下载视频</option>
                <option value="audio-only">仅下载音频</option>
                <option value="danmaku-only">仅下载弹幕</option>
                <option value="sub-only">仅下载字幕</option>
                <option value="cover-only">仅下载封面</option>
              </select>
            </div>
            <div class="field">
              <label for="api_mode">解析模式</label>
              <select id="api_mode">
                <option value="">默认</option>
                <option value="tv">TV 端</option>
                <option value="app">APP 端</option>
                <option value="intl">国际版</option>
              </select>
            </div>
            <div class="field">
              <label for="encoding_priority">视频编码优先级</label>
              <input id="encoding_priority" type="text" placeholder="例如：hevc,av1,avc">
            </div>
            <div class="field">
              <label for="language">音频语言</label>
              <input id="language" type="text" placeholder="例如：chi、jpn">
            </div>
            <div class="field">
              <label for="user_agent">User-Agent</label>
              <input id="user_agent" type="text" placeholder="留空则使用 BBDown 默认策略">
            </div>
            <div class="field">
              <label for="cookie_text">Cookie / SESSDATA</label>
              <input id="cookie_text" type="text" placeholder="留空则不额外传 cookie">
              <small>需要会员权限或登录态时可填；支持完整 cookie 字符串或你自己整理后的 cookie。</small>
            </div>
            <div class="field">
              <label for="access_token">Access Token</label>
              <input id="access_token" type="text" placeholder="TV / APP 接口需要时可填写">
            </div>
            <div class="checkbox-row">
              <label><input id="download_danmaku" type="checkbox"> 同时下载弹幕</label>
              <label><input id="skip_subtitle" type="checkbox"> 跳过字幕</label>
              <label><input id="skip_cover" type="checkbox"> 跳过封面</label>
              <label><input id="use_aria2c" type="checkbox"> 使用 aria2c</label>
              <label><input id="use_mp4box" type="checkbox"> 使用 MP4Box 混流</label>
              <label><input id="skip_mux" type="checkbox"> 跳过混流</label>
              <label><input id="hide_streams" type="checkbox"> 隐藏可用流信息</label>
              <label><input id="debug_mode" type="checkbox"> 输出调试日志</label>
              <label><input id="download_ai_subtitle" type="checkbox"> 下载 AI 字幕</label>
              <label><input id="video_ascending" type="checkbox"> 视频升序</label>
              <label><input id="audio_ascending" type="checkbox"> 音频升序</label>
              <label><input id="allow_pcdn" type="checkbox"> 允许 PCDN</label>
              <label><input id="save_archives_to_file" type="checkbox"> 记录已下载视频</label>
            </div>
            <div class="field">
              <label for="ffmpeg_path">ffmpeg 路径</label>
              <input id="ffmpeg_path" type="text" placeholder="留空则走系统 PATH">
            </div>
            <div class="field">
              <label for="mp4box_path">MP4Box 路径</label>
              <input id="mp4box_path" type="text" placeholder="使用 MP4Box 时可指定路径">
            </div>
            <div class="field">
              <label for="aria2c_path">aria2c 路径</label>
              <input id="aria2c_path" type="text" placeholder="留空则走系统 PATH">
            </div>
            <div class="field">
              <label for="aria2c_args">aria2c 附加参数</label>
              <input id="aria2c_args" type="text" placeholder='例如：--max-concurrent-downloads=8'>
            </div>
            <div class="field">
              <label for="delay_per_page">合集每 P 间隔秒数</label>
              <input id="delay_per_page" type="text" placeholder="例如：2">
            </div>
            <div class="field">
              <label for="file_pattern">单 P 文件名模板</label>
              <input id="file_pattern" type="text" placeholder='例如：&lt;videoTitle&gt;-&lt;dfn&gt;'>
            </div>
            <div class="field">
              <label for="multi_file_pattern">多 P 文件名模板</label>
              <input id="multi_file_pattern" type="text" placeholder='例如：&lt;videoTitle&gt;/[P&lt;pageNumberWithZero&gt;]&lt;pageTitle&gt;'>
            </div>
            <div class="field">
              <label for="work_dir_override">工作目录覆盖</label>
              <input id="work_dir_override" type="text" placeholder='例如：D:\\Downloads'>
              <small>会覆盖上面的“下载目录”设置。</small>
            </div>
            <div class="field">
              <label for="upos_host">UPOS Host</label>
              <input id="upos_host" type="text" placeholder="例如：upos-sz-mirrorcos.bilivideo.com">
            </div>
            <div class="field">
              <label for="bili_host">BiliPlus Host</label>
              <input id="bili_host" type="text" placeholder="例如：https://www.biliplus.com">
            </div>
            <div class="field">
              <label for="ep_host">EP Host</label>
              <input id="ep_host" type="text" placeholder="代理番剧 season 接口时可填写">
            </div>
            <div class="field">
              <label for="area">Area</label>
              <input id="area" type="text" placeholder="hk / tw / th">
            </div>
            <div class="field">
              <label for="config_file">配置文件</label>
              <input id="config_file" type="text" placeholder="例如：BBDown.config">
            </div>
            <div class="field">
              <label for="extra_args">额外 BBDown 参数</label>
              <input id="extra_args" type="text" placeholder='例如：--work-dir "D:\\Downloads"'>
              <small>这里可补充网页里暂时没单独做控件的 BBDown 参数。</small>
            </div>
          </div>
          <div class="actions">
            <button class="secondary" id="fetch_quality_btn" type="button">获取画质</button>
            <button class="primary" id="download_btn" type="submit">开始下载</button>
            <button class="secondary" id="download_example_btn" type="button">填入示例</button>
          </div>
        </form>
      </section>
    </div>

    <section class="card" style="margin-top: 18px;">
      <h2>批量任务队列</h2>
      <div class="field">
        <label for="batch_urls">批量链接 / BV / av / ep / ss</label>
        <textarea id="batch_urls" rows="8" style="width:100%;padding:12px;border-radius:12px;border:1px solid var(--panel-border);background:var(--input-bg);color:var(--text);font:inherit;resize:vertical;" placeholder="每行一个链接、BV 号或分享文本&#10;https://www.bilibili.com/video/BV...&#10;BV1494y1C72o&#10;https://www.bilibili.com/bangumi/play/ss..."></textarea>
        <small>支持一行一个链接顺序执行；也支持直接粘贴标题加链接的分享文本。</small>
      </div>
      <div class="checkbox-row">
        <label><input id="batch_continue_on_error" type="checkbox" checked> 单个失败后继续后续任务</label>
      </div>
      <div class="actions">
        <button class="secondary" id="batch_example_btn" type="button">填入示例</button>
        <button class="primary" id="batch_run_btn" type="button">开始批量下载</button>
      </div>
    </section>

    <section class="card result-card">
      <h2>运行结果</h2>
      <div id="status" class="status">等待开始。</div>
      <div class="kv">
        <div>命令</div><div id="command">-</div>
        <div>退出码</div><div id="returncode">-</div>
        <div>时间</div><div id="finished_at">-</div>
      </div>
      <pre id="log">还没有运行记录。</pre>
      <div class="actions" style="margin-top: 14px;">
        <button class="secondary" id="copy_command_btn" type="button">复制命令</button>
        <button class="secondary" id="save_settings_btn" type="button">保存设置</button>
        <button class="secondary" id="clear_settings_btn" type="button">清除已保存设置</button>
        <button class="secondary" id="clear_log_btn" type="button">清空日志</button>
      </div>
      <div class="footer">
        启动地址：<span>$server_url</span><br>
        参考：<a href="https://github.com/nilaoda/BBDown" target="_blank" rel="noreferrer">BBDown</a>
      </div>
    </section>
  </div>

  <script>
    const statusEl = document.getElementById("status");
    const commandEl = document.getElementById("command");
    const returnCodeEl = document.getElementById("returncode");
    const finishedAtEl = document.getElementById("finished_at");
    const logEl = document.getElementById("log");
    const cacheRunBtn = document.getElementById("cache_run_btn");
    const fetchQualityBtn = document.getElementById("fetch_quality_btn");
    const downloadBtn = document.getElementById("download_btn");
    const videoUrlInput = document.getElementById("video_url");
    const toggleAdvancedBtn = document.getElementById("toggle_advanced_btn");
    const advancedDownloadOptions = document.getElementById("advanced_download_options");
    const refreshLoginBtn = document.getElementById("refresh_login_btn");
    const loginWebBtn = document.getElementById("login_web_btn");
    const loginTvBtn = document.getElementById("login_tv_btn");
    const clearLoginBtn = document.getElementById("clear_login_btn");
    const batchUrlsInput = document.getElementById("batch_urls");
    const batchContinueOnError = document.getElementById("batch_continue_on_error");
    const batchExampleBtn = document.getElementById("batch_example_btn");
    const batchRunBtn = document.getElementById("batch_run_btn");
    const loginStatusText = document.getElementById("login_status_text");
    const loginAccountName = document.getElementById("login_account_name");
    const loginUid = document.getElementById("login_uid");
    const loginType = document.getElementById("login_type");
    const loginExpiresAt = document.getElementById("login_expires_at");
    const loginStatusMessage = document.getElementById("login_status_message");
    const detectToolsBtn = document.getElementById("detect_tools_btn");
    const toolDetectMessage = document.getElementById("tool_detect_message");
    const toolDetectList = document.getElementById("tool_detect_list");
    const pagePickerPanel = document.getElementById("page_picker_panel");
    const pagePickerHint = document.getElementById("page_picker_hint");
    const pagePickerList = document.getElementById("page_picker_list");
    const pagePickerSelectAllBtn = document.getElementById("page_picker_select_all_btn");
    const pagePickerClearBtn = document.getElementById("page_picker_clear_btn");
    const pagePickerInvertBtn = document.getElementById("page_picker_invert_btn");
    const pagePickerRefreshBtn = document.getElementById("page_picker_refresh_btn");
    const copyCommandBtn = document.getElementById("copy_command_btn");
    const saveSettingsBtn = document.getElementById("save_settings_btn");
    const clearSettingsBtn = document.getElementById("clear_settings_btn");
    const STORAGE_KEY = "bilibili_media_webui_settings_v1";
    let currentPageItems = [];

    function setStatus(text, kind) {
      statusEl.textContent = text;
      statusEl.className = "status" + (kind ? " " + kind : "");
    }

    function setButtonsBusy(busy) {
      cacheRunBtn.disabled = busy;
      fetchQualityBtn.disabled = busy;
      downloadBtn.disabled = busy;
      batchRunBtn.disabled = busy;
      cacheRunBtn.textContent = busy ? "处理中..." : "开始转换";
      fetchQualityBtn.textContent = busy ? "处理中..." : "获取画质";
      downloadBtn.textContent = busy ? "处理中..." : "开始下载";
    }

    function updateResult(data, ok, fallbackMessage) {
      commandEl.textContent = data.command || "-";
      returnCodeEl.textContent = String(data.returncode ?? "-");
      finishedAtEl.textContent = data.finished_at || "-";
      logEl.textContent = [data.stdout, data.stderr].filter(Boolean).join("\\n") || "无输出";
      setStatus(ok ? fallbackMessage : (data.error || "操作失败，请看日志。"), ok ? "ok" : "error");
    }

    function updateLoginStatusCard(data) {
      const loggedIn = Boolean(data && data.logged_in);
      loginStatusText.textContent = loggedIn ? "已登录" : "未登录";
      loginAccountName.textContent = (data && data.account_name) || "-";
      loginUid.textContent = (data && data.uid) || "-";
      loginType.textContent = (data && data.login_type) || "-";
      loginExpiresAt.textContent = (data && data.expires_at) || "-";
      loginStatusMessage.textContent = (data && data.message) || "未获取到登录状态";
      loginStatusMessage.className = "status " + (loggedIn ? "ok" : "warn");
    }

    function renderToolDetection(data) {
      const tools = data && data.tools ? Object.values(data.tools) : [];
      toolDetectList.innerHTML = "";
      const statusKind = data && data.ok ? "ok" : "warn";
      toolDetectMessage.textContent = (data && data.message) || "暂未执行工具检测。";
      toolDetectMessage.className = "status " + statusKind;
      for (const tool of tools) {
        const card = document.createElement("div");
        card.className = "tool-status-item";

        const title = document.createElement("strong");
        title.textContent = tool.label || tool.key || "工具";
        card.appendChild(title);

        const status = document.createElement("div");
        status.textContent = tool.found ? "已找到 · " + (tool.source || "detected") : "未找到";
        card.appendChild(status);

        if (tool.version) {
          const version = document.createElement("small");
          version.textContent = tool.version;
          card.appendChild(version);
        }

        const path = document.createElement("code");
        path.textContent = tool.path || ((tool.searched && tool.searched[0]) || "未找到常见路径");
        card.appendChild(path);
        toolDetectList.appendChild(card);
      }
    }

    function applyDetectedToolPaths(fields, overwrite = false) {
      if (!fields) return;
      const placeholderValues = new Set(["BBDown", "BBDown.exe", "ffmpeg", "ffmpeg.exe", "ffprobe", "ffprobe.exe", "aria2c", "aria2c.exe", "MP4Box", "MP4Box.exe", "mp4box", "mp4box.exe"]);
      for (const [fieldName, fieldValue] of Object.entries(fields)) {
        const element = document.getElementById(fieldName);
        if (!element || !fieldValue) continue;
        const currentValue = String(element.value || "").trim();
        if (!overwrite && currentValue && !placeholderValues.has(currentValue)) continue;
        element.value = String(fieldValue);
      }
    }

    async function detectTools(showToast = false, overwrite = false) {
      try {
        const data = await postJsonSilent("/api/tool-detect", {
          bbdown_path: document.getElementById("bbdown_path").value.trim(),
          cache_ffmpeg: document.getElementById("cache_ffmpeg").value.trim(),
          cache_ffprobe: document.getElementById("cache_ffprobe").value.trim(),
          ffmpeg_path: document.getElementById("ffmpeg_path").value.trim(),
          mp4box_path: document.getElementById("mp4box_path").value.trim(),
          aria2c_path: document.getElementById("aria2c_path").value.trim(),
        });
        applyDetectedToolPaths(data.fields, overwrite);
        renderToolDetection(data);
        saveSettingsToLocalStorage(false);
        if (showToast) setStatus(data.message || "工具路径检测完成。", data.ok ? "ok" : "warn");
      } catch (error) {
        toolDetectMessage.textContent = "工具路径检测失败：" + String(error);
        toolDetectMessage.className = "status error";
        if (showToast) setStatus("工具路径检测失败：" + String(error), "error");
      }
    }

    function parsePageSpecIndexes(spec, totalCount) {
      const result = new Set();
      const raw = (spec || "").trim();
      if (!raw) return result;
      const upper = raw.toUpperCase();
      if (upper === "ALL") {
        for (let index = 1; index <= totalCount; index += 1) result.add(index);
        return result;
      }
      const segments = upper.split(",").map((segment) => segment.trim()).filter(Boolean);
      for (const segment of segments) {
        if (segment === "LAST") {
          if (totalCount > 0) result.add(totalCount);
          continue;
        }
        const rangeMatch = segment.match(/^(\\d+)-(\\d+)$$/);
        if (rangeMatch) {
          let start = Number(rangeMatch[1]);
          let end = Number(rangeMatch[2]);
          if (Number.isNaN(start) || Number.isNaN(end)) continue;
          if (start > end) [start, end] = [end, start];
          for (let index = start; index <= end; index += 1) {
            if (index >= 1 && index <= totalCount) result.add(index);
          }
          continue;
        }
        const index = Number(segment);
        if (!Number.isNaN(index) && index >= 1 && index <= totalCount) {
          result.add(index);
        }
      }
      return result;
    }

    function buildPageSpecFromIndexes(indexes, totalCount) {
      const sorted = Array.from(indexes).filter((value) => value >= 1 && value <= totalCount).sort((a, b) => a - b);
      if (!sorted.length) return "";
      if (sorted.length === totalCount) return "ALL";
      if (sorted.length === 1 && sorted[0] === totalCount) return "LAST";
      const parts = [];
      let start = sorted[0];
      let previous = sorted[0];
      for (let i = 1; i <= sorted.length; i += 1) {
        const value = sorted[i];
        if (value === previous + 1) {
          previous = value;
          continue;
        }
        parts.push(start === previous ? String(start) : String(start) + "-" + String(previous));
        start = value;
        previous = value;
      }
      return parts.join(",");
    }

    function updatePageSpecFromPicker() {
      const checkboxes = pagePickerList.querySelectorAll("input[type='checkbox'][data-page-index]");
      const indexes = new Set();
      for (const checkbox of checkboxes) {
        if (checkbox.checked) indexes.add(Number(checkbox.dataset.pageIndex));
      }
      document.getElementById("page_spec").value = buildPageSpecFromIndexes(indexes, currentPageItems.length);
      saveSettingsToLocalStorage(false);
    }

    function syncPickerFromPageSpec() {
      if (!currentPageItems.length) return;
      const selected = parsePageSpecIndexes(getPageSpec(), currentPageItems.length);
      const checkboxes = pagePickerList.querySelectorAll("input[type='checkbox'][data-page-index]");
      for (const checkbox of checkboxes) {
        checkbox.checked = selected.has(Number(checkbox.dataset.pageIndex));
      }
    }

    function renderPagePicker(items, meta = {}) {
      currentPageItems = Array.isArray(items) ? items : [];
      pagePickerList.innerHTML = "";
      if (!currentPageItems.length) {
        pagePickerPanel.classList.add("hidden");
        pagePickerHint.textContent = "当前链接暂未解析到分P / 剧集列表。";
        pagePickerHint.className = "status warn";
        return;
      }

      pagePickerPanel.classList.remove("hidden");
      const mediaTitle = meta && meta.title ? "《" + meta.title + "》" : "当前链接";
      const sourceText = meta && meta.source ? "数据源：" + meta.source : "已解析可选列表";
      pagePickerHint.textContent = mediaTitle + " 共解析到 " + currentPageItems.length + " 项。" + sourceText + "。勾选后会自动同步到“分P / 剧集范围”。";
      pagePickerHint.className = "status ok";

      const selected = parsePageSpecIndexes(getPageSpec(), currentPageItems.length);
      for (const item of currentPageItems) {
        const wrapper = document.createElement("label");
        wrapper.className = "page-picker-item";

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.dataset.pageIndex = String(item.index);
        checkbox.checked = selected.has(Number(item.index));
        checkbox.addEventListener("change", updatePageSpecFromPicker);

        const textWrap = document.createElement("div");
        const title = document.createElement("strong");
        title.textContent = item.label || (String(item.index) + ". " + (item.title || ""));
        textWrap.appendChild(title);

        const subtitle = document.createElement("small");
        subtitle.textContent = item.subtitle || item.title || "";
        textWrap.appendChild(subtitle);

        wrapper.appendChild(checkbox);
        wrapper.appendChild(textWrap);
        pagePickerList.appendChild(wrapper);
      }
    }

    function getAllFormSettings() {
      return {
        cache_input_path: document.getElementById("cache_input_path").value,
        cache_output: document.getElementById("cache_output").value,
        cache_ffmpeg: document.getElementById("cache_ffmpeg").value,
        cache_ffprobe: document.getElementById("cache_ffprobe").value,
        cache_force: document.getElementById("cache_force").checked,
        cache_dry_run: document.getElementById("cache_dry_run").checked,
        video_url: document.getElementById("video_url").value,
        download_output: document.getElementById("download_output").value,
        bbdown_path: document.getElementById("bbdown_path").value,
        quality_select: document.getElementById("quality_select").value,
        quality_custom: document.getElementById("quality_custom").value,
        page_spec: document.getElementById("page_spec").value,
        show_all_pages: document.getElementById("show_all_pages").checked,
        download_mode: document.getElementById("download_mode").value,
        api_mode: document.getElementById("api_mode").value,
        encoding_priority: document.getElementById("encoding_priority").value,
        language: document.getElementById("language").value,
        user_agent: document.getElementById("user_agent").value,
        cookie_text: document.getElementById("cookie_text").value,
        access_token: document.getElementById("access_token").value,
        download_danmaku: document.getElementById("download_danmaku").checked,
        skip_subtitle: document.getElementById("skip_subtitle").checked,
        skip_cover: document.getElementById("skip_cover").checked,
        use_aria2c: document.getElementById("use_aria2c").checked,
        use_mp4box: document.getElementById("use_mp4box").checked,
        skip_mux: document.getElementById("skip_mux").checked,
        hide_streams: document.getElementById("hide_streams").checked,
        debug_mode: document.getElementById("debug_mode").checked,
        download_ai_subtitle: document.getElementById("download_ai_subtitle").checked,
        video_ascending: document.getElementById("video_ascending").checked,
        audio_ascending: document.getElementById("audio_ascending").checked,
        allow_pcdn: document.getElementById("allow_pcdn").checked,
        save_archives_to_file: document.getElementById("save_archives_to_file").checked,
        ffmpeg_path: document.getElementById("ffmpeg_path").value,
        mp4box_path: document.getElementById("mp4box_path").value,
        aria2c_path: document.getElementById("aria2c_path").value,
        aria2c_args: document.getElementById("aria2c_args").value,
        delay_per_page: document.getElementById("delay_per_page").value,
        file_pattern: document.getElementById("file_pattern").value,
        multi_file_pattern: document.getElementById("multi_file_pattern").value,
        work_dir_override: document.getElementById("work_dir_override").value,
        upos_host: document.getElementById("upos_host").value,
        bili_host: document.getElementById("bili_host").value,
        ep_host: document.getElementById("ep_host").value,
        area: document.getElementById("area").value,
        config_file: document.getElementById("config_file").value,
        extra_args: document.getElementById("extra_args").value,
        batch_urls: batchUrlsInput.value,
        batch_continue_on_error: batchContinueOnError.checked,
        advanced_open: !advancedDownloadOptions.classList.contains("hidden"),
      };
    }

    function applySavedSettings(settings) {
      if (!settings) return;
      for (const [key, value] of Object.entries(settings)) {
        const element = document.getElementById(key);
        if (!element) continue;
        if (element.type === "checkbox") {
          element.checked = Boolean(value);
        } else {
          element.value = value ?? "";
        }
      }
      setAdvancedMode(Boolean(settings.advanced_open));
    }

    function saveSettingsToLocalStorage(showToast = false) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(getAllFormSettings()));
      if (showToast) setStatus("设置已保存到本地浏览器。", "ok");
    }

    function loadSettingsFromLocalStorage() {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return false;
      try {
        applySavedSettings(JSON.parse(raw));
        return true;
      } catch {
        localStorage.removeItem(STORAGE_KEY);
        return false;
      }
    }

    async function postJsonSilent(path, payload) {
      const response = await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      return response.json();
    }

    async function refreshLoginStatus(showToast = false) {
      const payload = {
        bbdown_path: document.getElementById("bbdown_path").value.trim(),
      };
      try {
        const data = await postJsonSilent("/api/login-status", payload);
        updateLoginStatusCard(data);
        if (showToast) {
          setStatus(data.logged_in ? "登录状态已刷新。" : "当前未登录。", data.logged_in ? "ok" : "warn");
        }
      } catch (error) {
        updateLoginStatusCard({
          logged_in: false,
          message: "获取登录状态失败：" + String(error),
        });
        if (showToast) setStatus("获取登录状态失败。", "error");
      }
    }

    async function startLogin(mode) {
      try {
        const data = await postJsonSilent("/api/login-start", {
          bbdown_path: document.getElementById("bbdown_path").value.trim(),
          mode,
        });
        updateLoginStatusCard({
          logged_in: false,
          message: data.message || "已打开登录窗口。",
          login_type: mode === "tv" ? "tv" : "web",
        });
        setStatus(data.message || "已打开登录窗口。", data.ok ? "ok" : "error");
      } catch (error) {
        setStatus("启动登录失败：" + String(error), "error");
      }
    }

    async function clearLoginData() {
      try {
        const data = await postJsonSilent("/api/login-clear", {
          bbdown_path: document.getElementById("bbdown_path").value.trim(),
        });
        updateLoginStatusCard(data.current_status || {
          logged_in: false,
          message: data.message || "已清除登录数据。",
        });
        setStatus(data.message || "已清除登录数据。", data.ok ? "ok" : "error");
      } catch (error) {
        setStatus("清除登录状态失败：" + String(error), "error");
      }
    }

    function getCommonDownloadPayload() {
      return {
        output: document.getElementById("download_output").value.trim(),
        bbdown_path: document.getElementById("bbdown_path").value.trim(),
        page_spec: getPageSpec(),
        show_all_pages: document.getElementById("show_all_pages").checked,
        ...getAdvancedDownloadOptions(),
      };
    }

    async function postJson(path, payload, successMessage) {
      setButtonsBusy(true);
      setStatus("正在执行，请稍等...");
      logEl.textContent = "运行中...";
      try {
        const response = await fetch(path, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await response.json();
        updateResult(data, response.ok && data.returncode === 0, successMessage);
        return data;
      } catch (error) {
        const data = {
          command: "-",
          returncode: "-",
          finished_at: new Date().toLocaleString(),
          stdout: "",
          stderr: String(error),
          error: "请求失败，请确认网页启动器仍在运行。",
        };
        updateResult(data, false, "");
        return null;
      } finally {
        setButtonsBusy(false);
      }
    }

    function getSelectedQuality() {
      const custom = document.getElementById("quality_custom").value.trim();
      if (custom) return custom;
      const value = document.getElementById("quality_select").value;
      if (value === "自动（最高可用）") return "";
      return value;
    }

    function getPageSpec() {
      const value = document.getElementById("page_spec").value.trim();
      if (!value) return "";
      const upperValue = value.toUpperCase();
      if (upperValue === "ALL" || upperValue === "LAST") return upperValue;
      return value.replace(/\\s+/g, "");
    }

    function setAdvancedMode(show) {
      advancedDownloadOptions.classList.toggle("hidden", !show);
      toggleAdvancedBtn.textContent = show ? "切换到简约模式" : "显示更多功能";
    }

    function getAdvancedDownloadOptions() {
      return {
        download_mode: document.getElementById("download_mode").value,
        api_mode: document.getElementById("api_mode").value,
        encoding_priority: document.getElementById("encoding_priority").value.trim(),
        language: document.getElementById("language").value.trim(),
        user_agent: document.getElementById("user_agent").value.trim(),
        cookie: document.getElementById("cookie_text").value.trim(),
        access_token: document.getElementById("access_token").value.trim(),
        download_danmaku: document.getElementById("download_danmaku").checked,
        skip_subtitle: document.getElementById("skip_subtitle").checked,
        skip_cover: document.getElementById("skip_cover").checked,
        use_aria2c: document.getElementById("use_aria2c").checked,
        use_mp4box: document.getElementById("use_mp4box").checked,
        skip_mux: document.getElementById("skip_mux").checked,
        hide_streams: document.getElementById("hide_streams").checked,
        debug_mode: document.getElementById("debug_mode").checked,
        download_ai_subtitle: document.getElementById("download_ai_subtitle").checked,
        video_ascending: document.getElementById("video_ascending").checked,
        audio_ascending: document.getElementById("audio_ascending").checked,
        allow_pcdn: document.getElementById("allow_pcdn").checked,
        save_archives_to_file: document.getElementById("save_archives_to_file").checked,
        ffmpeg_path: document.getElementById("ffmpeg_path").value.trim(),
        mp4box_path: document.getElementById("mp4box_path").value.trim(),
        aria2c_path: document.getElementById("aria2c_path").value.trim(),
        aria2c_args: document.getElementById("aria2c_args").value.trim(),
        delay_per_page: document.getElementById("delay_per_page").value.trim(),
        file_pattern: document.getElementById("file_pattern").value.trim(),
        multi_file_pattern: document.getElementById("multi_file_pattern").value.trim(),
        work_dir_override: document.getElementById("work_dir_override").value.trim(),
        upos_host: document.getElementById("upos_host").value.trim(),
        host: document.getElementById("bili_host").value.trim(),
        ep_host: document.getElementById("ep_host").value.trim(),
        area: document.getElementById("area").value.trim(),
        config_file: document.getElementById("config_file").value.trim(),
        extra_args: document.getElementById("extra_args").value.trim(),
      };
    }

    async function fetchVideoInfo(showHint = true) {
      const normalized = normalizeVideoInput(showHint);
      const data = await postJson("/api/url-info", {
        url: normalized || document.getElementById("video_url").value.trim(),
        bbdown_path: document.getElementById("bbdown_path").value.trim(),
        page_spec: getPageSpec(),
        show_all_pages: document.getElementById("show_all_pages").checked,
        ...getAdvancedDownloadOptions(),
      }, "画质信息获取完成。");

      if (!data) return null;
      if (data.normalized_url) {
        videoUrlInput.value = data.normalized_url;
      }
      if (Array.isArray(data.qualities) && data.qualities.length > 0) {
        populateQualityOptions(data.qualities);
      }
      renderPagePicker(data.pages || [], {
        title: data.media_title || "",
        source: data.pages_source || "",
      });

      if (Array.isArray(data.pages) && data.pages.length > 0) {
        setStatus("已解析出 " + data.pages.length + " 个分P / 剧集，可直接勾选。", "ok");
      } else if (Array.isArray(data.qualities) && data.qualities.length > 0) {
        setStatus("已解析出可选清晰度。", "ok");
      } else {
        setStatus("已拿到信息，但没有自动解析出分P或清晰度，请参考日志。", "warn");
      }
      return data;
    }

    function extractBilibiliTarget(rawText) {
      const text = (rawText || "").trim();
      if (!text) return "";

      const urlMatch = text.match(/https?:\\/\\/[^\\s"'<>]+/i);
      if (urlMatch) {
        return urlMatch[0].replace(/[)\\]}>,.;!?]+$$/u, "");
      }

      const idMatch = text.match(/\\b(BV[0-9A-Za-z]{10}|av\\d+|ep\\d+|ss\\d+)\\b/i);
      if (!idMatch) return text;

      const value = idMatch[1];
      const lowerValue = value.toLowerCase();
      if (lowerValue.startsWith("bv")) return "BV" + value.slice(2);
      if (lowerValue.startsWith("av")) return "av" + value.slice(2);
      return lowerValue;
    }

    function normalizeVideoInput(showHint = false) {
      const raw = videoUrlInput.value;
      const normalized = extractBilibiliTarget(raw);
      if (normalized && normalized !== raw.trim()) {
        videoUrlInput.value = normalized;
        if (showHint) setStatus("已自动识别出视频链接。", "ok");
      }
      return normalized;
    }

    function populateQualityOptions(qualities) {
      const select = document.getElementById("quality_select");
      const existing = new Set();
      const values = ["自动（最高可用）"];
      for (const option of select.options) {
        const value = option.value;
        if (!existing.has(value)) {
          existing.add(value);
          values.push(value);
        }
      }
      for (const quality of qualities || []) {
        if (!existing.has(quality)) {
          existing.add(quality);
          values.push(quality);
        }
      }
      select.innerHTML = "";
      for (const value of values) {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        select.appendChild(option);
      }
    }

    document.getElementById("cache-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      await postJson("/api/cache-run", {
        input_path: document.getElementById("cache_input_path").value.trim(),
        output: document.getElementById("cache_output").value.trim(),
        ffmpeg: document.getElementById("cache_ffmpeg").value.trim(),
        ffprobe: document.getElementById("cache_ffprobe").value.trim(),
        force: document.getElementById("cache_force").checked,
        dry_run: document.getElementById("cache_dry_run").checked,
      }, "转换完成。");
    });

    document.getElementById("fetch_quality_btn").addEventListener("click", async () => {
      await fetchVideoInfo(true);
    });

    document.getElementById("download-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const normalized = normalizeVideoInput(true);
      const data = await postJson("/api/url-download", {
        url: normalized || document.getElementById("video_url").value.trim(),
        output: document.getElementById("download_output").value.trim(),
        bbdown_path: document.getElementById("bbdown_path").value.trim(),
        quality: getSelectedQuality(),
        page_spec: getPageSpec(),
        show_all_pages: document.getElementById("show_all_pages").checked,
        ...getAdvancedDownloadOptions(),
      }, "下载完成。");
      if (data && data.normalized_url) {
        videoUrlInput.value = data.normalized_url;
      }
    });

    document.getElementById("cache_example_btn").addEventListener("click", () => {
      document.getElementById("cache_input_path").value = "$default_cache_path_example";
      document.getElementById("cache_output").value = "";
      document.getElementById("cache_ffmpeg").value = "ffmpeg";
      document.getElementById("cache_ffprobe").value = "";
      document.getElementById("cache_force").checked = true;
      document.getElementById("cache_dry_run").checked = false;
      setStatus("已填入缓存目录示例。", "warn");
    });

    document.getElementById("download_example_btn").addEventListener("click", () => {
      document.getElementById("video_url").value = "https://www.bilibili.com/video/BV1494y1C72o";
      document.getElementById("download_output").value = "";
      document.getElementById("bbdown_path").value = "$default_bbdown_example";
      document.getElementById("quality_custom").value = "";
      document.getElementById("page_spec").value = "ALL";
      document.getElementById("show_all_pages").checked = true;
      document.getElementById("quality_select").value = "1080P 高清";
      document.getElementById("download_mode").value = "sub-only";
      document.getElementById("api_mode").value = "";
      document.getElementById("encoding_priority").value = "";
      document.getElementById("language").value = "";
      document.getElementById("user_agent").value = "";
      document.getElementById("cookie_text").value = "";
      document.getElementById("access_token").value = "";
      document.getElementById("download_danmaku").checked = false;
      document.getElementById("skip_subtitle").checked = false;
      document.getElementById("skip_cover").checked = false;
      document.getElementById("use_aria2c").checked = false;
      document.getElementById("use_mp4box").checked = false;
      document.getElementById("skip_mux").checked = false;
      document.getElementById("hide_streams").checked = false;
      document.getElementById("debug_mode").checked = false;
      document.getElementById("download_ai_subtitle").checked = false;
      document.getElementById("video_ascending").checked = false;
      document.getElementById("audio_ascending").checked = false;
      document.getElementById("allow_pcdn").checked = false;
      document.getElementById("save_archives_to_file").checked = false;
      document.getElementById("ffmpeg_path").value = "";
      document.getElementById("mp4box_path").value = "";
      document.getElementById("aria2c_path").value = "";
      document.getElementById("aria2c_args").value = "";
      document.getElementById("delay_per_page").value = "";
      document.getElementById("file_pattern").value = "";
      document.getElementById("multi_file_pattern").value = "";
      document.getElementById("work_dir_override").value = "";
      document.getElementById("upos_host").value = "";
      document.getElementById("bili_host").value = "";
      document.getElementById("ep_host").value = "";
      document.getElementById("area").value = "";
      document.getElementById("config_file").value = "";
      document.getElementById("extra_args").value = "";
      setAdvancedMode(true);
      setStatus("已填入链接下载示例。", "warn");
    });

    toggleAdvancedBtn.addEventListener("click", () => {
      setAdvancedMode(advancedDownloadOptions.classList.contains("hidden"));
    });

    refreshLoginBtn.addEventListener("click", async () => {
      await refreshLoginStatus(true);
    });

    loginWebBtn.addEventListener("click", async () => {
      await startLogin("web");
    });

    loginTvBtn.addEventListener("click", async () => {
      await startLogin("tv");
    });

    clearLoginBtn.addEventListener("click", async () => {
      await clearLoginData();
    });

    detectToolsBtn.addEventListener("click", async () => {
      await detectTools(true, true);
    });

    pagePickerSelectAllBtn.addEventListener("click", () => {
      pagePickerList.querySelectorAll("input[type='checkbox'][data-page-index]").forEach((checkbox) => {
        checkbox.checked = true;
      });
      updatePageSpecFromPicker();
    });

    pagePickerClearBtn.addEventListener("click", () => {
      pagePickerList.querySelectorAll("input[type='checkbox'][data-page-index]").forEach((checkbox) => {
        checkbox.checked = false;
      });
      updatePageSpecFromPicker();
    });

    pagePickerInvertBtn.addEventListener("click", () => {
      pagePickerList.querySelectorAll("input[type='checkbox'][data-page-index]").forEach((checkbox) => {
        checkbox.checked = !checkbox.checked;
      });
      updatePageSpecFromPicker();
    });

    pagePickerRefreshBtn.addEventListener("click", async () => {
      await fetchVideoInfo(true);
    });

    batchExampleBtn.addEventListener("click", () => {
      batchUrlsInput.value = [
        "https://www.bilibili.com/video/BV1494y1C72o",
        "BV1494y1C72o",
        "【示例分享文本】https://www.bilibili.com/video/BV1494y1C72o?vd_source=330f8fe25b57ed8ec864c0f881472669",
      ].join("\\n");
      setStatus("已填入批量任务示例。", "warn");
      saveSettingsToLocalStorage(false);
    });

    batchRunBtn.addEventListener("click", async () => {
      const urlsText = batchUrlsInput.value.trim();
      if (!urlsText) {
        setStatus("请先填写至少一条批量链接。", "warn");
        return;
      }
      await postJson("/api/url-batch", {
        urls_text: urlsText,
        batch_continue_on_error: batchContinueOnError.checked,
        quality: getSelectedQuality(),
        ...getCommonDownloadPayload(),
      }, "批量任务执行完成。");
    });

    videoUrlInput.addEventListener("blur", () => {
      normalizeVideoInput(true);
    });

    videoUrlInput.addEventListener("paste", () => {
      window.setTimeout(() => normalizeVideoInput(true), 0);
    });

    document.getElementById("page_spec").addEventListener("change", syncPickerFromPageSpec);
    document.getElementById("page_spec").addEventListener("blur", syncPickerFromPageSpec);

    copyCommandBtn.addEventListener("click", async () => {
      const command = commandEl.textContent || "";
      if (!command || command === "-") {
        setStatus("当前没有可复制的命令。", "warn");
        return;
      }
      try {
        await navigator.clipboard.writeText(command);
        setStatus("命令已复制到剪贴板。", "ok");
      } catch (error) {
        setStatus("复制命令失败：" + String(error), "error");
      }
    });

    saveSettingsBtn.addEventListener("click", () => {
      saveSettingsToLocalStorage(true);
    });

    clearSettingsBtn.addEventListener("click", () => {
      localStorage.removeItem(STORAGE_KEY);
      setStatus("已清除浏览器中保存的设置。", "warn");
    });

    document.querySelectorAll("input, select, textarea").forEach((element) => {
      element.addEventListener("change", () => saveSettingsToLocalStorage(false));
      element.addEventListener("blur", () => saveSettingsToLocalStorage(false));
    });

    document.getElementById("clear_log_btn").addEventListener("click", () => {
      commandEl.textContent = "-";
      returnCodeEl.textContent = "-";
      finishedAtEl.textContent = "-";
      logEl.textContent = "还没有运行记录。";
      setStatus("日志已清空。");
    });

    if (!loadSettingsFromLocalStorage()) {
      setAdvancedMode(false);
    }
    detectTools(false, false);
    refreshLoginStatus(false);
  </script>
</body>
</html>
"""
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="启动 Bilibili 下载 / 转换的本地网页界面。")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址，默认 127.0.0.1")
    parser.add_argument("--port", type=int, default=8767, help="监听端口，默认 8767")
    parser.add_argument("--no-open", action="store_true", help="启动后不自动打开浏览器")
    return parser.parse_args()


def html_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def js_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def render_quality_options() -> str:
    return "\n".join(
        f'<option value="{html_escape(quality)}">{html_escape(quality)}</option>' for quality in QUALITY_OPTIONS
    )


def apply_direct_connection_env(env: dict[str, str]) -> None:
    for key in PROXY_ENV_KEYS:
        env.pop(key, None)

    no_proxy_values: list[str] = []
    seen: set[str] = set()
    for key in ("NO_PROXY", "no_proxy"):
        for part in str(env.get(key, "") or "").split(","):
            value = part.strip()
            if not value:
                continue
            lowered = value.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            no_proxy_values.append(value)

    for host in DEFAULT_NO_PROXY_HOSTS:
        lowered = host.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        no_proxy_values.append(host)

    no_proxy_value = ",".join(no_proxy_values)
    env["NO_PROXY"] = no_proxy_value
    env["no_proxy"] = no_proxy_value


def build_process_env(prefer_system_dotnet: bool = False, disable_proxy: bool = False) -> dict[str, str]:
    env = os.environ.copy()
    if prefer_system_dotnet and SYSTEM_DOTNET_ROOT.exists():
        env["DOTNET_ROOT"] = str(SYSTEM_DOTNET_ROOT)
        env["DOTNET_ROOT_X64"] = str(SYSTEM_DOTNET_ROOT)
        env.pop("DOTNET_ROOT(x86)", None)
    if disable_proxy:
        apply_direct_connection_env(env)
    return env


def run_subprocess(
    command: list[str],
    cwd: Path | None = None,
    prefer_system_dotnet: bool = False,
    disable_proxy: bool = False,
) -> dict:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd or REPO_ROOT),
            env=build_process_env(prefer_system_dotnet=prefer_system_dotnet, disable_proxy=disable_proxy),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return {
            "command": subprocess.list2cmdline(command),
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    except FileNotFoundError as exc:
        return {
            "command": subprocess.list2cmdline(command),
            "returncode": 127,
            "stdout": "",
            "stderr": str(exc),
            "error": f"未找到可执行文件: {command[0]}",
            "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


def extract_qualities(text: str) -> list[str]:
    return [q for q in VALID_QUALITIES if q in text]


def format_duration_text(seconds: int | float | str | None) -> str:
    try:
        total_seconds = int(float(seconds or 0))
    except (TypeError, ValueError):
        return ""
    if total_seconds <= 0:
        return ""
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:d}:{secs:02d}"


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
                items.append(
                    {
                        "index": index,
                        "title": title,
                        "subtitle": duration,
                        "label": f"P{index} · {title}" if title else f"P{index}",
                    }
                )
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
                items.append(
                    {
                        "index": index,
                        "title": title,
                        "subtitle": duration,
                        "label": f"P{index} · {title}" if title else f"P{index}",
                    }
                )
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
                    items.append(
                        {
                            "index": index,
                            "title": title,
                            "subtitle": " · ".join(subtitle_parts),
                            "label": f"{index}. {title}" if title else f"{index}.",
                        }
                    )

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
            items.append(
                {
                    "index": index,
                    "title": title,
                    "subtitle": "",
                    "label": f"{index}. {title}",
                }
            )
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
        if not download_ai_subtitle:
            command.append("--skip-ai")
        if video_ascending:
            command.append("--video-ascending")
        if audio_ascending:
            command.append("--audio-ascending")
        if allow_pcdn:
            command.append("--allow-pcdn")
        if skip_mux:
            command.append("--skip-mux")
        if use_aria2c:
            command.append("--use-aria2c")
        if aria2c_path:
            command.extend(["--aria2c-path", aria2c_path])
        if aria2c_args:
            command.extend(["--aria2c-args", aria2c_args])

    extend_with_extra_args(command, extra_args)

    return {
        "page_spec": page_spec,
        "show_all_pages": show_all_pages,
        "api_mode": api_mode,
        "encoding_priority": encoding_priority,
        "language": language,
        "user_agent": user_agent,
        "download_mode": download_mode,
        "download_danmaku": download_danmaku,
        "skip_subtitle": skip_subtitle,
        "skip_cover": skip_cover,
        "use_aria2c": use_aria2c,
        "use_mp4box": use_mp4box,
        "skip_mux": skip_mux,
        "hide_streams": hide_streams,
        "debug_mode": debug_mode,
        "download_ai_subtitle": download_ai_subtitle,
        "video_ascending": video_ascending,
        "audio_ascending": audio_ascending,
        "allow_pcdn": allow_pcdn,
        "save_archives_to_file": save_archives_to_file,
        "ffmpeg_path": ffmpeg_path,
        "mp4box_path": mp4box_path,
        "aria2c_path": aria2c_path,
        "aria2c_args": aria2c_args,
        "delay_per_page": delay_per_page,
        "file_pattern": file_pattern,
        "multi_file_pattern": multi_file_pattern,
        "work_dir_override": work_dir_override,
        "upos_host": upos_host,
        "host": host,
        "ep_host": ep_host,
        "area": area,
        "config_file": config_file,
        "extra_args": extra_args,
        "has_cookie": bool(cookie),
        "has_access_token": bool(access_token),
    }


def resolve_executable_path(command: str) -> Path | None:
    if not command.strip():
        return None
    direct_path = Path(command).expanduser()
    if direct_path.exists():
        return direct_path.resolve()
    found = shutil.which(command)
    return Path(found).resolve() if found else None


@functools.lru_cache(maxsize=None)
def get_scoop_roots() -> tuple[Path, ...]:
    roots: list[Path] = []
    for env_name in ("SCOOP", "SCOOP_GLOBAL"):
        value = os.environ.get(env_name, "").strip()
        if value:
            roots.append(Path(value))
    roots.extend(
        [
            Path.home() / "scoop",
            Path(r"D:\workspaces\Scoop"),
        ]
    )
    unique_roots: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root).lower()
        if key not in seen:
            seen.add(key)
            unique_roots.append(root)
    return tuple(unique_roots)


def iter_tool_candidates(tool_key: str) -> list[Path]:
    home = Path.home()
    local_app_data = Path(os.environ.get("LOCALAPPDATA", ""))
    program_files = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    program_files_x86 = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
    scoop_roots = get_scoop_roots()
    candidates: list[Path] = []

    if tool_key == "bbdown":
        candidates.extend(
            [
                home / ".dotnet" / "tools" / "BBDown.exe",
                home / ".dotnet" / "tools" / "BBDown",
            ]
        )
        for root in scoop_roots:
            candidates.extend(
                [
                    root / "shims" / "BBDown.exe",
                    root / "apps" / "bbdown" / "current" / "BBDown.exe",
                ]
            )
    elif tool_key in {"ffmpeg", "ffprobe"}:
        executable = f"{tool_key}.exe"
        for root in scoop_roots:
            candidates.extend(
                [
                    root / "shims" / executable,
                    root / "apps" / "ffmpeg" / "current" / "bin" / executable,
                ]
            )
        candidates.extend(
            [
                program_files / "ffmpeg" / "bin" / executable,
                program_files_x86 / "ffmpeg" / "bin" / executable,
            ]
        )
    elif tool_key == "aria2c":
        for root in scoop_roots:
            candidates.extend(
                [
                    root / "shims" / "aria2c.exe",
                    root / "apps" / "aria2" / "current" / "aria2c.exe",
                ]
            )
        candidates.extend(
            [
                program_files / "aria2" / "aria2c.exe",
                program_files_x86 / "aria2" / "aria2c.exe",
            ]
        )
    elif tool_key == "mp4box":
        candidates.extend(
            [
                program_files / "GPAC" / "MP4Box.exe",
                program_files_x86 / "GPAC" / "MP4Box.exe",
            ]
        )
        for root in scoop_roots:
            candidates.extend(
                [
                    root / "shims" / "mp4box.exe",
                    root / "shims" / "MP4Box.exe",
                    root / "apps" / "gpac" / "current" / "MP4Box.exe",
                ]
            )
        if local_app_data:
            candidates.append(local_app_data / "Programs" / "GPAC" / "MP4Box.exe")

    unique_candidates: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate).lower()
        if key not in seen:
            seen.add(key)
            unique_candidates.append(candidate)
    return unique_candidates


def probe_tool_version(tool_key: str, executable: Path) -> str:
    version_args = {
        "bbdown": ["-v"],
        "ffmpeg": ["-version"],
        "ffprobe": ["-version"],
        "aria2c": ["-v"],
        "mp4box": ["-version"],
    }.get(tool_key, ["--version"])
    result = run_subprocess(
        [str(executable), *version_args],
        cwd=executable.parent,
        prefer_system_dotnet=tool_key == "bbdown",
        disable_proxy=tool_key == "bbdown",
    )
    version_text = str(result.get("stdout", "") or "").strip() or str(result.get("stderr", "") or "").strip()
    if not version_text:
        return ""
    return version_text.splitlines()[0].strip()


def detect_single_tool(tool_key: str, configured_path: str = "") -> dict[str, object]:
    aliases = {
        "bbdown": ["BBDown", "BBDown.exe"],
        "ffmpeg": ["ffmpeg", "ffmpeg.exe"],
        "ffprobe": ["ffprobe", "ffprobe.exe"],
        "aria2c": ["aria2c", "aria2c.exe"],
        "mp4box": ["MP4Box", "MP4Box.exe", "mp4box", "mp4box.exe"],
    }.get(tool_key, [])
    searched: list[str] = []

    if configured_path.strip():
        resolved = resolve_executable_path(configured_path)
        if resolved:
            return {
                "key": tool_key,
                "label": TOOL_LABELS.get(tool_key, tool_key),
                "found": True,
                "path": str(resolved),
                "source": "configured",
                "version": probe_tool_version(tool_key, resolved),
            }
        searched.append(configured_path)

    for alias in aliases:
        resolved = resolve_executable_path(alias)
        if resolved:
            return {
                "key": tool_key,
                "label": TOOL_LABELS.get(tool_key, tool_key),
                "found": True,
                "path": str(resolved),
                "source": "path",
                "version": probe_tool_version(tool_key, resolved),
            }
        searched.append(alias)

    for candidate in iter_tool_candidates(tool_key):
        if candidate.exists():
            return {
                "key": tool_key,
                "label": TOOL_LABELS.get(tool_key, tool_key),
                "found": True,
                "path": str(candidate.resolve()),
                "source": "common-location",
                "version": probe_tool_version(tool_key, candidate.resolve()),
            }
        searched.append(str(candidate))

    return {
        "key": tool_key,
        "label": TOOL_LABELS.get(tool_key, tool_key),
        "found": False,
        "path": "",
        "source": "",
        "version": "",
        "searched": searched[:8],
    }


def detect_tool_paths(payload: dict) -> dict[str, object]:
    configured_values = {
        "bbdown": str(payload.get("bbdown_path", "")).strip(),
        "ffmpeg": str(payload.get("ffmpeg_path", "")).strip() or str(payload.get("cache_ffmpeg", "")).strip(),
        "ffprobe": str(payload.get("cache_ffprobe", "")).strip(),
        "aria2c": str(payload.get("aria2c_path", "")).strip(),
        "mp4box": str(payload.get("mp4box_path", "")).strip(),
    }
    tools = {tool_key: detect_single_tool(tool_key, configured_values.get(tool_key, "")) for tool_key in TOOL_LABELS}
    fields: dict[str, str] = {}
    for tool_key, field_names in TOOL_FIELD_BINDINGS.items():
        detected_path = str(tools[tool_key].get("path", "") or "")
        if not detected_path:
            continue
        for field_name in field_names:
            fields[field_name] = detected_path

    found_count = sum(1 for item in tools.values() if item.get("found"))
    if found_count == len(tools):
        message = "已检测到全部常用工具路径。"
    elif found_count:
        message = f"已检测到 {found_count}/{len(tools)} 个工具，其余工具可继续使用系统 PATH 或手动填写。"
    else:
        message = "暂未检测到常用工具，请检查是否已安装，或继续手动填写。"

    return {
        "ok": found_count > 0,
        "message": message,
        "tools": tools,
        "fields": fields,
        "found_count": found_count,
        "total_count": len(tools),
    }


def get_bbdown_data_candidates(bbdown_path: str) -> list[Path]:
    candidates: list[Path] = []
    resolved = resolve_executable_path(bbdown_path)
    if resolved:
        base_dir = resolved.parent
        candidates.extend(
            [
                base_dir / "BBDown.data",
                base_dir / "BBDownTV.data",
                base_dir / "BBDownApp.data",
            ]
        )

    user_home = Path.home()
    candidates.extend(
        [
            user_home / ".dotnet" / "tools" / "BBDown.data",
            user_home / ".dotnet" / "tools" / "BBDownTV.data",
            user_home / ".dotnet" / "tools" / "BBDownApp.data",
        ]
    )

    unique_candidates: list[Path] = []
    seen: set[str] = set()
    for item in candidates:
        key = str(item).lower()
        if key not in seen:
            seen.add(key)
            unique_candidates.append(item)
    return unique_candidates


def parse_cookie_string(cookie_text: str) -> dict[str, str]:
    cookies: dict[str, str] = {}
    for part in cookie_text.split(";"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        cookies[key.strip()] = value.strip()
    return cookies


def read_cookie_data_file(path: Path) -> tuple[str, dict[str, str]]:
    cookie_text = path.read_text(encoding="utf-8", errors="ignore").strip()
    return cookie_text, parse_cookie_string(cookie_text)


def format_expire_time(raw_expire: str) -> str:
    if not raw_expire.isdigit():
        return ""
    try:
        return datetime.fromtimestamp(int(raw_expire)).strftime("%Y-%m-%d %H:%M:%S")
    except (OverflowError, ValueError, OSError):
        return ""


def build_bbdown_command(payload: dict, url: str, for_info: bool = False) -> tuple[list[str], Path, dict[str, object]]:
    bbdown_path = str(payload.get("bbdown_path", "")).strip() or DEFAULT_BBDOWN
    command = [bbdown_path, url]
    if for_info:
        command.append("--only-show-info")
    else:
        quality = str(payload.get("quality", "")).strip()
        if quality:
            command.extend(["--dfn-priority", quality])
    option_result = extend_bbdown_options(command, payload, for_info=for_info)
    work_dir = REPO_ROOT
    if not for_info:
        output = str(payload.get("output", "")).strip()
        if output:
            work_dir = ensure_output_dir(output)
    return command, work_dir, option_result


def split_batch_targets(raw_text: str) -> list[str]:
    targets: list[str] = []
    seen: set[str] = set()
    for raw_line in raw_text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        normalized = normalize_video_target(stripped)
        if not normalized:
            continue
        if normalized not in seen:
            seen.add(normalized)
            targets.append(normalized)
    return targets


def clear_bbdown_login_data(bbdown_path: str) -> dict[str, object]:
    deleted_files: list[str] = []
    missing_files: list[str] = []
    errors: list[str] = []

    for data_path in get_bbdown_data_candidates(bbdown_path):
        try:
            if data_path.exists():
                try:
                    os.chmod(data_path, 0o666)
                except OSError:
                    pass
                data_path.unlink()
                deleted_files.append(str(data_path))
            else:
                missing_files.append(str(data_path))
        except OSError as exc:
            errors.append(f"{data_path}: {exc}")

    current_status = get_bbdown_login_status(bbdown_path)
    if errors:
        message = "清除登录数据时出现部分错误。"
    elif deleted_files:
        message = f"已清除 {len(deleted_files)} 个登录数据文件。"
    else:
        message = "未找到可清除的登录数据文件。"

    return {
        "ok": not errors,
        "message": message,
        "deleted_files": deleted_files,
        "missing_files": missing_files,
        "errors": errors,
        "current_status": current_status,
    }


def _process_single_target(payload: dict, index: int, target: str) -> dict[str, object]:
    item_payload = dict(payload)
    command, work_dir, option_result = build_bbdown_command(item_payload, target, for_info=False)
    result = run_subprocess(command, cwd=work_dir, prefer_system_dotnet=True, disable_proxy=True)
    result["normalized_url"] = target
    result["index"] = index
    result.update(option_result)
    return result


def run_batch_downloads(payload: dict) -> dict[str, object]:
    targets = split_batch_targets(str(payload.get("urls_text", "")))
    if not targets:
        return {
            "command": "-",
            "returncode": 1,
            "stdout": "",
            "stderr": "",
            "error": "请先填写至少一条批量链接。",
            "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": [],
            "targets": [],
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "skipped": 0,
        }

    continue_on_error = bool(payload.get("batch_continue_on_error"))
    items: list[dict[str, object]] = []
    command_lines: list[str] = []
    stdout_blocks: list[str] = []
    stderr_blocks: list[str] = []
    failed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for index, target in enumerate(targets, start=1):
            futures.append(executor.submit(_process_single_target, payload, index, target))

        for future in futures:
            result = future.result()
            target = str(result.get("normalized_url", ""))
            index = int(result.get("index", 0))

            items.append(result)
            command_lines.append(f"[{index}] {result.get('command', '')}")

            stdout_text = str(result.get("stdout", "") or "").strip()
            stderr_text = str(result.get("stderr", "") or "").strip()
            error_text = str(result.get("error", "") or "").strip()
            title = f"===== [{index}/{len(targets)}] {target} ====="
            stdout_blocks.append(title + (f"\n{stdout_text}" if stdout_text else ""))
            combined_error = stderr_text
            if error_text and error_text not in combined_error:
                combined_error = (combined_error + "\n" if combined_error else "") + error_text
            if combined_error:
                stderr_blocks.append(title + f"\n{combined_error}")

            if result.get("returncode") != 0:
                failed += 1
                if not continue_on_error:
                    for pending_future in futures:
                        pending_future.cancel()
                    break

    processed = len(items)
    skipped = len(targets) - processed
    succeeded = processed - failed
    stopped_early = skipped > 0
    returncode = 0 if failed == 0 and not stopped_early else 1

    if returncode == 0:
        message = f"批量任务共 {len(targets)} 项，全部完成。"
    elif failed and stopped_early:
        message = f"批量任务在 {processed}/{len(targets)} 项后停止，失败 {failed} 项。"
    else:
        message = f"批量任务完成，成功 {succeeded} 项，失败 {failed} 项，跳过 {skipped} 项。"

    result: dict[str, object] = {
        "command": "\n".join(command_lines) if command_lines else "-",
        "returncode": returncode,
        "stdout": "\n\n".join(stdout_blocks),
        "stderr": "\n\n".join(stderr_blocks),
        "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": items,
        "targets": targets,
        "processed": processed,
        "succeeded": succeeded,
        "failed": failed,
        "skipped": skipped,
        "continue_on_error": continue_on_error,
        "message": message,
    }
    if returncode != 0:
        result["error"] = message
    return result


def fetch_bilibili_nav_info(cookie_text: str) -> dict[str, object]:
    request = urllib_request.Request(
        "https://api.bilibili.com/x/web-interface/nav",
        headers={
            "Cookie": cookie_text,
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.bilibili.com/",
        },
    )
    with urllib_request.urlopen(request, timeout=8) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        return {}
    data = payload.get("data")
    return data if isinstance(data, dict) else {}


def get_bbdown_login_status(bbdown_path: str) -> dict[str, object]:
    status: dict[str, object] = {
        "logged_in": False,
        "login_type": "",
        "account_name": "",
        "uid": "",
        "expires_at": "",
        "data_file": "",
        "message": "未检测到登录信息",
        "raw_cookie_found": False,
    }

    for data_path in get_bbdown_data_candidates(bbdown_path):
        if not data_path.exists():
            continue

        cookie_text, cookies = read_cookie_data_file(data_path)
        if not cookies:
            continue

        login_type = "web"
        filename = data_path.name.lower()
        if "tv" in filename:
            login_type = "tv"
        elif "app" in filename:
            login_type = "app"

        status.update(
            {
                "logged_in": True,
                "login_type": login_type,
                "uid": cookies.get("DedeUserID", ""),
                "expires_at": format_expire_time(cookies.get("Expires", "")),
                "data_file": str(data_path),
                "message": "已检测到登录数据",
                "raw_cookie_found": True,
            }
        )

        if login_type == "web":
            try:
                nav_data = fetch_bilibili_nav_info(cookie_text)
                if nav_data:
                    status["logged_in"] = bool(nav_data.get("isLogin", True))
                    status["account_name"] = str(nav_data.get("uname", "") or "")
                    status["uid"] = str(nav_data.get("mid", "") or status["uid"])
                    if status["logged_in"]:
                        status["message"] = "网页登录有效"
                    else:
                        status["message"] = "检测到登录数据，但当前未处于登录状态"
            except Exception as exc:
                status["message"] = f"已检测到登录数据，但获取账号信息失败：{exc}"
        return status

    return status


def start_bbdown_login_process(bbdown_path: str, mode: str) -> dict[str, object]:
    executable = resolve_executable_path(bbdown_path)
    if executable is None:
        return {
            "ok": False,
            "message": f"未找到 BBDown 可执行文件：{bbdown_path}",
        }

    login_arg = "login" if mode == "web" else "logintv"
    command = [str(executable), login_arg]
    try:
        process = subprocess.Popen(
            command,
            cwd=str(executable.parent),
            env=build_process_env(prefer_system_dotnet=True, disable_proxy=True),
            creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
        )
    except Exception as exc:
        return {
            "ok": False,
            "message": f"启动登录窗口失败：{exc}",
            "command": subprocess.list2cmdline(command),
        }

    return {
        "ok": True,
        "message": "已打开登录窗口，请按窗口提示扫码登录；登录完成后点击“刷新登录状态”。",
        "command": subprocess.list2cmdline(command),
        "pid": process.pid,
        "mode": mode,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "BilibiliMediaWebUI/1.0"

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._send_common_headers()
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/bootstrap":
            self._send_json(self.server.build_bootstrap_payload())  # type: ignore[attr-defined]
            return
        if parsed.path in {"/", "/index.html"}:
            frontend_index = self.server.get_frontend_index_path()  # type: ignore[attr-defined]
            if frontend_index is not None:
                self._send_file(frontend_index)
                return
            html = self.server.render_html()  # type: ignore[attr-defined]
            self._send_html(html)
            return
        if parsed.path == "/healthz":
            self._send_json({"ok": True})
            return
        frontend_asset = self.server.resolve_frontend_asset(parsed.path)  # type: ignore[attr-defined]
        if frontend_asset is not None:
            self._send_file(frontend_asset)
            return
        if parsed.path.startswith("/api/"):
            self._send_json({"error": "Not Found"}, status=HTTPStatus.NOT_FOUND)
            return
        if self.server.get_frontend_index_path() is not None and not Path(parsed.path).suffix:  # type: ignore[attr-defined]
            self._send_file(self.server.get_frontend_index_path())  # type: ignore[attr-defined]
            return
        if parsed.path == "/favicon.ico":
            self.send_response(HTTPStatus.NO_CONTENT)
            self._send_common_headers()
            self.end_headers()
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        payload = self._read_json_body()
        if payload is None:
            self._send_json({"error": "请求体不是合法 JSON"}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == "/api/cache-run":
            self._handle_cache_run(payload)
            return
        if parsed.path == "/api/tool-detect":
            self._handle_tool_detect(payload)
            return
        if parsed.path == "/api/login-status":
            self._handle_login_status(payload)
            return
        if parsed.path == "/api/login-start":
            self._handle_login_start(payload)
            return
        if parsed.path == "/api/login-clear":
            self._handle_login_clear(payload)
            return
        if parsed.path == "/api/url-info":
            self._handle_url_info(payload)
            return
        if parsed.path == "/api/url-download":
            self._handle_url_download(payload)
            return
        if parsed.path == "/api/url-batch":
            self._handle_url_batch(payload)
            return
        self._send_json({"error": "Not Found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _handle_cache_run(self, payload: dict) -> None:
        input_path = str(payload.get("input_path", "")).strip()
        if not input_path:
            self._send_json({"error": "请填写缓存目录"}, status=HTTPStatus.BAD_REQUEST)
            return

        command = [sys.executable, "-B", str(CACHE_CONVERTER_SCRIPT), input_path]
        output = str(payload.get("output", "")).strip()
        ffmpeg = str(payload.get("ffmpeg", "")).strip()
        ffprobe = str(payload.get("ffprobe", "")).strip()

        if output:
            command.extend(["--output", output])
        if ffmpeg:
            command.extend(["--ffmpeg", ffmpeg])
        if ffprobe:
            command.extend(["--ffprobe", ffprobe])
        if payload.get("force"):
            command.append("--force")
        if payload.get("dry_run"):
            command.append("--dry-run")

        result = run_subprocess(command, cwd=REPO_ROOT)
        status = HTTPStatus.OK if result["returncode"] == 0 else HTTPStatus.BAD_REQUEST
        if result["returncode"] != 0 and "error" not in result:
            result["error"] = "缓存转换失败，请查看日志。"
        self._send_json(result, status=status)

    def _handle_tool_detect(self, payload: dict) -> None:
        self._send_json(detect_tool_paths(payload), status=HTTPStatus.OK)

    def _handle_login_status(self, payload: dict) -> None:
        bbdown_path = str(payload.get("bbdown_path", "")).strip() or DEFAULT_BBDOWN
        status_info = get_bbdown_login_status(bbdown_path)
        self._send_json(status_info, status=HTTPStatus.OK)

    def _handle_login_start(self, payload: dict) -> None:
        bbdown_path = str(payload.get("bbdown_path", "")).strip() or DEFAULT_BBDOWN
        mode = str(payload.get("mode", "")).strip().lower()
        if mode not in {"web", "tv"}:
            self._send_json({"ok": False, "message": "mode 仅支持 web 或 tv"}, status=HTTPStatus.BAD_REQUEST)
            return
        result = start_bbdown_login_process(bbdown_path, mode)
        status = HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST
        self._send_json(result, status=status)


    def _handle_login_clear(self, payload: dict) -> None:
        bbdown_path = str(payload.get("bbdown_path", "")).strip() or DEFAULT_BBDOWN
        result = clear_bbdown_login_data(bbdown_path)
        status = HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST
        self._send_json(result, status=status)

    def _handle_url_info(self, payload: dict) -> None:
        raw_url = str(payload.get("url", "")).strip()
        url = normalize_video_target(raw_url)
        bbdown_path = str(payload.get("bbdown_path", "")).strip() or DEFAULT_BBDOWN
        if not url:
            self._send_json({"error": "请填写视频链接"}, status=HTTPStatus.BAD_REQUEST)
            return

        command = [bbdown_path, url, "--only-show-info"]
        option_result = extend_bbdown_options(command, payload, for_info=True)
        result = run_subprocess(command, cwd=REPO_ROOT, prefer_system_dotnet=True, disable_proxy=True)
        combined = "\n".join(filter(None, [result.get("stdout", ""), result.get("stderr", "")]))
        result["qualities"] = extract_qualities(combined)
        page_items, media_title, pages_source = fetch_page_items_from_bilibili_api(url, payload)
        if not page_items:
            page_items = extract_page_items_from_text(combined)
            if page_items:
                pages_source = "bbdown-output"
        result["pages"] = page_items
        result["pages_source"] = pages_source
        result["media_title"] = media_title
        result["normalized_url"] = url
        result.update(option_result)
        status = HTTPStatus.OK if result["returncode"] == 0 else HTTPStatus.BAD_REQUEST
        if result["returncode"] != 0 and "error" not in result:
            result["error"] = "获取画质信息失败，请确认 BBDown 已安装并且链接可访问。"
        self._send_json(result, status=status)

    def _handle_url_download(self, payload: dict) -> None:
        raw_url = str(payload.get("url", "")).strip()
        url = normalize_video_target(raw_url)
        bbdown_path = str(payload.get("bbdown_path", "")).strip() or DEFAULT_BBDOWN
        output = str(payload.get("output", "")).strip()
        quality = str(payload.get("quality", "")).strip()

        if not url:
            self._send_json({"error": "请填写视频链接"}, status=HTTPStatus.BAD_REQUEST)
            return

        command = [bbdown_path, url]
        if quality:
            command.extend(["--dfn-priority", quality])
        option_result = extend_bbdown_options(command, payload, for_info=False)

        work_dir = REPO_ROOT
        if output:
            work_dir = ensure_output_dir(output)

        result = run_subprocess(command, cwd=work_dir, prefer_system_dotnet=True, disable_proxy=True)
        result["normalized_url"] = url
        result.update(option_result)
        status = HTTPStatus.OK if result["returncode"] == 0 else HTTPStatus.BAD_REQUEST
        if result["returncode"] != 0 and "error" not in result:
            result["error"] = "下载失败，请确认 BBDown / ffmpeg 可用，以及所选清晰度可用。"
        self._send_json(result, status=status)


    def _handle_url_batch(self, payload: dict) -> None:
        if not str(payload.get("urls_text", "")).strip():
            self._send_json({"error": "请先填写至少一条批量链接。"}, status=HTTPStatus.BAD_REQUEST)
            return
        result = run_batch_downloads(payload)
        status = HTTPStatus.OK if result.get("returncode") == 0 else HTTPStatus.BAD_REQUEST
        self._send_json(result, status=status)

    def _read_json_body(self) -> dict | None:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        return data if isinstance(data, dict) else None

    def _send_common_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def _send_html(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self._send_common_headers()
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_file(self, path: Path, status: HTTPStatus = HTTPStatus.OK) -> None:
        content = path.read_bytes()
        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
            content_type = f"{content_type}; charset=utf-8"
        self.send_response(status)
        self._send_common_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._send_common_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


class WebServer(ThreadingHTTPServer):
    def __init__(self, host: str, port: int) -> None:
        super().__init__((host, port), Handler)
        self.host = host
        self.port = port
        self.frontend_dist_dir = FRONTEND_DIST_DIR

    def build_bootstrap_payload(self) -> dict[str, object]:
        return {
            "default_cache_path": DEFAULT_CACHE_PATH,
            "default_bbdown": DEFAULT_BBDOWN,
            "quality_options": QUALITY_OPTIONS,
            "server_url": f"http://{self.host}:{self.port}",
            "frontend_dist_ready": self.get_frontend_index_path() is not None,
        }

    def get_frontend_index_path(self) -> Path | None:
        index_path = self.frontend_dist_dir / "index.html"
        if index_path.exists():
            return index_path
        return None

    def resolve_frontend_asset(self, request_path: str) -> Path | None:
        if not request_path or request_path == "/":
            return None
        relative_path = request_path.lstrip("/")
        candidate = (self.frontend_dist_dir / relative_path).resolve()
        dist_root = self.frontend_dist_dir.resolve()
        try:
            candidate.relative_to(dist_root)
        except ValueError:
            return None
        if candidate.exists() and candidate.is_file():
            return candidate
        return None

    def render_html(self) -> str:
        return HTML_TEMPLATE.substitute(
            default_cache_path=html_escape(DEFAULT_CACHE_PATH),
            default_cache_path_example=js_escape(DEFAULT_CACHE_PATH),
            default_bbdown=html_escape(DEFAULT_BBDOWN),
            default_bbdown_example=js_escape(DEFAULT_BBDOWN),
            quality_options_html=render_quality_options(),
            server_url=f"http://{self.host}:{self.port}",
        )


def main() -> int:
    if not CACHE_CONVERTER_SCRIPT.exists():
        print(f"[ERROR] 未找到转换脚本: {CACHE_CONVERTER_SCRIPT}")
        return 1

    args = parse_args()
    server = WebServer(args.host, args.port)
    url = f"http://{args.host}:{args.port}"

    print(f"[INFO] 启动成功: {url}")
    print("[INFO] 模式一：缓存目录转 MP4")
    print("[INFO] 模式二：B 站链接下载（依赖 BBDown）")
    print("[INFO] 按 Ctrl+C 可停止服务")

    if not args.no_open:
        threading.Thread(target=lambda: webbrowser.open(url), daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] 已停止。")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
