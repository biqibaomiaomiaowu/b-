<script setup lang="ts">
import { computed, onMounted, reactive, ref, shallowRef } from 'vue'

import { getJson, postJson } from '@/api/client'
import BatchQueuePanel from '@/components/batch/BatchQueuePanel.vue'
import CacheConverterPanel from '@/components/cache/CacheConverterPanel.vue'
import DownloadPanel from '@/components/download/DownloadPanel.vue'
import ResultPanel from '@/components/ResultPanel.vue'
import { useOperationState } from '@/composables/useOperationState'
import { usePersistentWorkspace } from '@/composables/usePersistentWorkspace'
import {
  createDefaultBatchForm,
  createDefaultCacheForm,
  createDefaultDownloadForm,
  createEmptyLoginStatus,
  FALLBACK_BOOTSTRAP,
  getBatchExample,
  getCacheExample,
  getDownloadExample,
  mergeQualityOptions,
} from '@/lib/defaults'
import { normalizePageSpec } from '@/lib/pageSpec'
import { extractBilibiliTarget } from '@/lib/video'
import type {
  BootstrapResponse,
  LoginStatus,
  OperationResult,
  PageItem,
  PagePickerMeta,
  ToolDetectResponse,
} from '@/types/api'

const bootstrap = shallowRef<BootstrapResponse>(FALLBACK_BOOTSTRAP)
const qualityOptions = ref<string[]>([...FALLBACK_BOOTSTRAP.quality_options])

const cacheForm = reactive(createDefaultCacheForm(FALLBACK_BOOTSTRAP.default_cache_path))
const downloadForm = reactive(createDefaultDownloadForm(FALLBACK_BOOTSTRAP.default_bbdown))
const batchForm = reactive(createDefaultBatchForm())

const loginStatus = reactive(createEmptyLoginStatus())
const toolDetection = shallowRef<ToolDetectResponse | null>(null)
const pageItems = ref<PageItem[]>([])
const pageMeta = reactive<PagePickerMeta>({
  title: '',
  source: '',
})

const { busy, statusText, statusKind, result, setStatus, applyResult, setPending, clearResult } = useOperationState()
const persistence = usePersistentWorkspace({ cacheForm, downloadForm, batchForm }, setStatus)

const serverUrl = computed(() => bootstrap.value.server_url || FALLBACK_BOOTSTRAP.server_url)
const selectedQuality = computed(() => {
  const customQuality = downloadForm.qualityCustom.trim()
  if (customQuality) {
    return customQuality
  }
  return downloadForm.qualitySelect === '自动（最高可用）' ? '' : downloadForm.qualitySelect
})

function buildNetworkFailure(error: unknown): OperationResult {
  return {
    command: '-',
    returncode: '-',
    finished_at: new Date().toLocaleString('zh-CN'),
    stdout: '',
    stderr: String(error),
    error: '请求失败，请确认后端服务仍在运行。',
  }
}

function normalizeCurrentVideoUrl(showHint = false) {
  const normalized = extractBilibiliTarget(downloadForm.videoUrl)
  if (normalized && normalized !== downloadForm.videoUrl.trim()) {
    downloadForm.videoUrl = normalized
    if (showHint) {
      setStatus('已自动识别出视频链接。', 'ok')
    }
  }
  return normalized
}

function buildCommonDownloadPayload() {
  return {
    output: downloadForm.output.trim(),
    bbdown_path: downloadForm.bbdownPath.trim(),
    page_spec: normalizePageSpec(downloadForm.pageSpec),
    show_all_pages: downloadForm.showAllPages,
    download_mode: downloadForm.advanced.downloadMode,
    api_mode: downloadForm.advanced.apiMode,
    encoding_priority: downloadForm.advanced.encodingPriority.trim(),
    language: downloadForm.advanced.language.trim(),
    user_agent: downloadForm.advanced.userAgent.trim(),
    cookie: downloadForm.advanced.cookieText.trim(),
    access_token: downloadForm.advanced.accessToken.trim(),
    download_danmaku: downloadForm.advanced.downloadDanmaku,
    skip_subtitle: downloadForm.advanced.skipSubtitle,
    skip_cover: downloadForm.advanced.skipCover,
    use_aria2c: downloadForm.advanced.useAria2c,
    use_mp4box: downloadForm.advanced.useMp4box,
    skip_mux: downloadForm.advanced.skipMux,
    hide_streams: downloadForm.advanced.hideStreams,
    debug_mode: downloadForm.advanced.debugMode,
    download_ai_subtitle: downloadForm.advanced.downloadAiSubtitle,
    video_ascending: downloadForm.advanced.videoAscending,
    audio_ascending: downloadForm.advanced.audioAscending,
    allow_pcdn: downloadForm.advanced.allowPcdn,
    save_archives_to_file: downloadForm.advanced.saveArchivesToFile,
    ffmpeg_path: downloadForm.advanced.ffmpegPath.trim(),
    mp4box_path: downloadForm.advanced.mp4boxPath.trim(),
    aria2c_path: downloadForm.advanced.aria2cPath.trim(),
    aria2c_args: downloadForm.advanced.aria2cArgs.trim(),
    delay_per_page: downloadForm.advanced.delayPerPage.trim(),
    file_pattern: downloadForm.advanced.filePattern.trim(),
    multi_file_pattern: downloadForm.advanced.multiFilePattern.trim(),
    work_dir_override: downloadForm.advanced.workDirOverride.trim(),
    upos_host: downloadForm.advanced.uposHost.trim(),
    host: downloadForm.advanced.biliHost.trim(),
    ep_host: downloadForm.advanced.epHost.trim(),
    area: downloadForm.advanced.area.trim(),
    config_file: downloadForm.advanced.configFile.trim(),
    extra_args: downloadForm.advanced.extraArgs.trim(),
  }
}

function applyDetectedField(fieldName: string, fieldValue: string, overwrite = false) {
  const placeholderValues = new Set([
    'BBDown',
    'BBDown.exe',
    'ffmpeg',
    'ffmpeg.exe',
    'ffprobe',
    'ffprobe.exe',
    'aria2c',
    'aria2c.exe',
    'MP4Box',
    'MP4Box.exe',
    'mp4box',
    'mp4box.exe',
  ])

  const readCurrent = () => {
    switch (fieldName) {
      case 'bbdown_path':
        return downloadForm.bbdownPath
      case 'cache_ffmpeg':
        return cacheForm.ffmpeg
      case 'cache_ffprobe':
        return cacheForm.ffprobe
      case 'ffmpeg_path':
        return downloadForm.advanced.ffmpegPath
      case 'mp4box_path':
        return downloadForm.advanced.mp4boxPath
      case 'aria2c_path':
        return downloadForm.advanced.aria2cPath
      default:
        return ''
    }
  }

  const writeCurrent = () => {
    switch (fieldName) {
      case 'bbdown_path':
        downloadForm.bbdownPath = fieldValue
        return
      case 'cache_ffmpeg':
        cacheForm.ffmpeg = fieldValue
        return
      case 'cache_ffprobe':
        cacheForm.ffprobe = fieldValue
        return
      case 'ffmpeg_path':
        downloadForm.advanced.ffmpegPath = fieldValue
        return
      case 'mp4box_path':
        downloadForm.advanced.mp4boxPath = fieldValue
        return
      case 'aria2c_path':
        downloadForm.advanced.aria2cPath = fieldValue
        return
      default:
        return
    }
  }

  const currentValue = readCurrent().trim()
  if (!overwrite && currentValue && !placeholderValues.has(currentValue)) {
    return
  }
  writeCurrent()
}

async function runOperation(path: string, payload: unknown, successMessage: string) {
  busy.value = true
  setStatus('正在执行，请稍等...')
  setPending()
  try {
    const response = await postJson<OperationResult>(path, payload)
    applyResult(response.data, response.ok && response.data.returncode === 0, successMessage)
    return response.data
  } catch (error) {
    applyResult(buildNetworkFailure(error), false, '')
    return null
  } finally {
    busy.value = false
  }
}

async function runCacheConversion() {
  await runOperation(
    '/api/cache-run',
    {
      input_path: cacheForm.inputPath.trim(),
      output: cacheForm.output.trim(),
      ffmpeg: cacheForm.ffmpeg.trim(),
      ffprobe: cacheForm.ffprobe.trim(),
      force: cacheForm.force,
      dry_run: cacheForm.dryRun,
    },
    '转换完成。',
  )
}

async function fetchVideoInfo(showHint = true) {
  const normalized = normalizeCurrentVideoUrl(showHint)
  const data = await runOperation(
    '/api/url-info',
    {
      url: normalized || downloadForm.videoUrl.trim(),
      ...buildCommonDownloadPayload(),
    },
    '画质信息获取完成。',
  )

  if (!data) {
    return null
  }

  if (data.normalized_url) {
    downloadForm.videoUrl = data.normalized_url
  }
  if (Array.isArray(data.qualities)) {
    qualityOptions.value = mergeQualityOptions(qualityOptions.value, data.qualities)
  }

  pageItems.value = Array.isArray(data.pages) ? data.pages : []
  pageMeta.title = data.media_title || ''
  pageMeta.source = data.pages_source || ''

  if (pageItems.value.length) {
    setStatus(`已解析出 ${pageItems.value.length} 个分 P / 剧集，可直接勾选。`, 'ok')
  } else if (Array.isArray(data.qualities) && data.qualities.length) {
    setStatus('已解析出可选清晰度。', 'ok')
  } else {
    setStatus('已拿到信息，但没有自动解析出分 P 或清晰度，请参考日志。', 'warn')
  }

  return data
}

async function runDownload() {
  const normalized = normalizeCurrentVideoUrl(true)
  const data = await runOperation(
    '/api/url-download',
    {
      url: normalized || downloadForm.videoUrl.trim(),
      quality: selectedQuality.value,
      ...buildCommonDownloadPayload(),
    },
    '下载完成。',
  )

  if (data?.normalized_url) {
    downloadForm.videoUrl = data.normalized_url
  }
}

async function runBatchDownload() {
  if (!batchForm.urlsText.trim()) {
    setStatus('请先填写至少一条批量链接。', 'warn')
    return
  }

  await runOperation(
    '/api/url-batch',
    {
      urls_text: batchForm.urlsText.trim(),
      batch_continue_on_error: batchForm.continueOnError,
      quality: selectedQuality.value,
      ...buildCommonDownloadPayload(),
    },
    '批量任务执行完成。',
  )
}

async function refreshLoginStatus(showToast = false) {
  try {
    const response = await postJson<LoginStatus>('/api/login-status', {
      bbdown_path: downloadForm.bbdownPath.trim(),
    })
    Object.assign(loginStatus, response.data)
    if (showToast) {
      setStatus(response.data.logged_in ? '登录状态已刷新。' : '当前未登录。', response.data.logged_in ? 'ok' : 'warn')
    }
  } catch (error) {
    Object.assign(loginStatus, {
      ...createEmptyLoginStatus(),
      message: `获取登录状态失败：${String(error)}`,
    })
    if (showToast) {
      setStatus('获取登录状态失败。', 'error')
    }
  }
}

async function startLogin(mode: 'web' | 'tv') {
  try {
    const response = await postJson<{ ok?: boolean; message?: string }>('/api/login-start', {
      bbdown_path: downloadForm.bbdownPath.trim(),
      mode,
    })
    Object.assign(loginStatus, {
      ...loginStatus,
      logged_in: false,
      login_type: mode,
      message: response.data.message || '已打开登录窗口。',
    })
    setStatus(response.data.message || '已打开登录窗口。', response.ok ? 'ok' : 'error')
  } catch (error) {
    setStatus(`启动登录失败：${String(error)}`, 'error')
  }
}

async function clearLoginData() {
  try {
    const response = await postJson<{ ok?: boolean; message?: string; current_status?: LoginStatus }>('/api/login-clear', {
      bbdown_path: downloadForm.bbdownPath.trim(),
    })
    Object.assign(loginStatus, response.data.current_status || createEmptyLoginStatus())
    setStatus(response.data.message || '已清除登录数据。', response.ok ? 'ok' : 'error')
  } catch (error) {
    setStatus(`清除登录状态失败：${String(error)}`, 'error')
  }
}

async function detectTools(showToast = false, overwrite = false) {
  try {
    const response = await postJson<ToolDetectResponse>('/api/tool-detect', {
      bbdown_path: downloadForm.bbdownPath.trim(),
      cache_ffmpeg: cacheForm.ffmpeg.trim(),
      cache_ffprobe: cacheForm.ffprobe.trim(),
      ffmpeg_path: downloadForm.advanced.ffmpegPath.trim(),
      mp4box_path: downloadForm.advanced.mp4boxPath.trim(),
      aria2c_path: downloadForm.advanced.aria2cPath.trim(),
    })

    toolDetection.value = response.data
    for (const [fieldName, fieldValue] of Object.entries(response.data.fields || {})) {
      applyDetectedField(fieldName, fieldValue, overwrite)
    }
    if (showToast) {
      setStatus(response.data.message || '工具路径检测完成。', response.data.ok ? 'ok' : 'warn')
    }
  } catch (error) {
    if (showToast) {
      setStatus(`工具路径检测失败：${String(error)}`, 'error')
    }
  }
}

function fillCacheExample() {
  Object.assign(cacheForm, getCacheExample(bootstrap.value.default_cache_path))
  setStatus('已填入缓存目录示例。', 'warn')
}

function fillDownloadExample() {
  const example = getDownloadExample(bootstrap.value.default_bbdown)
  Object.assign(downloadForm, {
    ...example,
    advanced: downloadForm.advanced,
  })
  Object.assign(downloadForm.advanced, example.advanced)
  qualityOptions.value = mergeQualityOptions(bootstrap.value.quality_options, [example.qualitySelect])
  setStatus('已填入链接下载示例。', 'warn')
}

function fillBatchExample() {
  Object.assign(batchForm, getBatchExample())
  setStatus('已填入批量任务示例。', 'warn')
}

async function copyCommand() {
  const commandText = String(result.command || '').trim()
  if (!commandText || commandText === '-') {
    setStatus('当前没有可复制的命令。', 'warn')
    return
  }

  try {
    await navigator.clipboard.writeText(commandText)
    setStatus('命令已复制到剪贴板。', 'ok')
  } catch (error) {
    setStatus(`复制命令失败：${String(error)}`, 'error')
  }
}

async function bootstrapWorkspace() {
  try {
    const response = await getJson<BootstrapResponse>('/api/bootstrap')
    if (response.ok) {
      bootstrap.value = {
        ...FALLBACK_BOOTSTRAP,
        ...response.data,
        quality_options: mergeQualityOptions(FALLBACK_BOOTSTRAP.quality_options, response.data.quality_options || []),
      }
    }
  } catch {
    bootstrap.value = FALLBACK_BOOTSTRAP
  }

  qualityOptions.value = [...bootstrap.value.quality_options]
  persistence.hydrate({
    defaultCachePath: bootstrap.value.default_cache_path,
    defaultBbdown: bootstrap.value.default_bbdown,
  })
  qualityOptions.value = mergeQualityOptions(qualityOptions.value, [downloadForm.qualitySelect])

  await Promise.allSettled([detectTools(false, false), refreshLoginStatus(false)])
}

onMounted(() => {
  void bootstrapWorkspace()
})
</script>

<template>
  <main class="workspace">
    <section class="hero-card">
      <div class="hero-copy">
        <p class="hero-eyebrow">Vue 3 + Python API</p>
        <h1 class="hero-title">Bilibili 下载 / 转换工作台</h1>
        <p class="hero-text">
          前端已改为 Vue 3 工程化结构，后端只负责本地 API、工具探测和静态资源分发。开发时可用 Vite 代理，生产时可直接由 Python 服务托管构建产物。
        </p>
        <div class="hero-pill-row">
          <span class="hero-pill">本地执行</span>
          <span class="hero-pill">工具自动探测</span>
          <span class="hero-pill">下载与转码分流</span>
        </div>
      </div>
      <div class="hero-stage">
        <div class="hero-flow-card">
          <p class="flow-eyebrow">Workflow</p>
          <div class="flow-steps">
            <div class="flow-step">
              <span class="flow-index">01</span>
              <div>
                <strong>解析链接</strong>
                <p>自动识别 BV / av / ep / ss、清晰度和分 P。</p>
              </div>
            </div>
            <div class="flow-step">
              <span class="flow-index">02</span>
              <div>
                <strong>执行任务</strong>
                <p>下载、缓存转码、批量队列统一走本地 API。</p>
              </div>
            </div>
            <div class="flow-step">
              <span class="flow-index">03</span>
              <div>
                <strong>保留结果</strong>
                <p>命令、日志和偏好设置留在当前工作台。</p>
              </div>
            </div>
          </div>
        </div>

        <div class="hero-metrics">
          <article class="metric-card">
            <span class="metric-label">当前服务</span>
            <strong class="metric-value">{{ serverUrl }}</strong>
          </article>
          <article class="metric-card">
            <span class="metric-label">默认 BBDown</span>
            <strong class="metric-value">{{ bootstrap.default_bbdown }}</strong>
          </article>
          <article class="metric-card metric-card--accent">
            <span class="metric-label">预置清晰度</span>
            <strong class="metric-value">{{ qualityOptions.length }} 项</strong>
          </article>
        </div>
      </div>
    </section>

    <section class="content-grid">
      <div class="main-column">
        <div class="dual-grid">
          <CacheConverterPanel v-model="cacheForm" :busy="busy" @run="runCacheConversion" @fill-example="fillCacheExample" />
          <DownloadPanel
            v-model="downloadForm"
            :busy="busy"
            :quality-options="qualityOptions"
            :login-status="loginStatus"
            :tool-detection="toolDetection"
            :page-items="pageItems"
            :page-meta="pageMeta"
            @fetch-info="fetchVideoInfo"
            @run-download="runDownload"
            @fill-example="fillDownloadExample"
            @refresh-login="refreshLoginStatus(true)"
            @login-web="startLogin('web')"
            @login-tv="startLogin('tv')"
            @clear-login="clearLoginData"
            @detect-tools="detectTools(true, true)"
          />
        </div>

        <BatchQueuePanel v-model="batchForm" :busy="busy" @run="runBatchDownload" @fill-example="fillBatchExample" />
      </div>

      <aside class="result-column">
        <p class="column-label">Session</p>
        <ResultPanel
          :status-text="statusText"
          :status-kind="statusKind"
          :result="result"
          :server-url="serverUrl"
          @copy-command="copyCommand"
          @save-settings="persistence.save(true)"
          @clear-settings="persistence.clear"
          @clear-log="clearResult"
        />
      </aside>
    </section>
  </main>
</template>

<style scoped>
.workspace {
  width: min(1480px, calc(100vw - 32px));
  margin: 0 auto;
  padding: 30px 0 42px;
}

.hero-card {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(380px, 0.95fr);
  gap: 22px;
  padding: 32px;
  border-radius: var(--radius-2xl);
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(239, 246, 252, 0.84)),
    radial-gradient(circle at top right, rgba(14, 91, 216, 0.14), transparent 34%);
  border: 1px solid rgba(34, 67, 96, 0.12);
  box-shadow: var(--shadow-strong);
  backdrop-filter: blur(18px);
  position: relative;
  overflow: hidden;
  animation: floatUp 420ms ease both;
}

.hero-card::before {
  content: "";
  position: absolute;
  inset: 0 auto auto 0;
  width: 220px;
  height: 220px;
  background: radial-gradient(circle, rgba(220, 122, 48, 0.12), transparent 70%);
  transform: translate(-24%, -28%);
  pointer-events: none;
}

.hero-copy {
  display: grid;
  gap: 16px;
  align-content: start;
}

.hero-eyebrow {
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--accent-strong);
}

.hero-title {
  margin: 0;
  max-width: 11ch;
  font-family: var(--font-display);
  font-size: clamp(36px, 5vw, 62px);
  line-height: 0.98;
  letter-spacing: 0.01em;
}

.hero-text {
  margin: 0;
  max-width: 58ch;
  font-size: 16px;
  line-height: 1.9;
  color: var(--muted);
}

.hero-pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-pill {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(34, 67, 96, 0.08);
  color: var(--accent-strong);
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 10px 24px rgba(29, 56, 79, 0.06);
}

.hero-stage {
  display: grid;
  gap: 14px;
}

.hero-flow-card {
  display: grid;
  gap: 14px;
  padding: 20px;
  border-radius: 30px;
  background:
    linear-gradient(160deg, rgba(9, 36, 78, 0.96), rgba(18, 61, 120, 0.9)),
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.14), transparent 30%);
  color: #edf4ff;
  box-shadow: 0 22px 40px rgba(14, 40, 73, 0.22);
}

.flow-eyebrow {
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(237, 244, 255, 0.72);
}

.flow-steps {
  display: grid;
  gap: 12px;
}

.flow-step {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

.flow-step strong {
  display: block;
  margin-bottom: 4px;
  font-size: 15px;
}

.flow-step p {
  margin: 0;
  color: rgba(237, 244, 255, 0.74);
  line-height: 1.6;
  font-size: 13px;
}

.flow-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff2df;
  font-family: var(--font-display);
  font-size: 15px;
  letter-spacing: 0.08em;
}

.hero-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.metric-card {
  display: grid;
  gap: 8px;
  min-height: 118px;
  padding: 18px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(34, 67, 96, 0.1);
  box-shadow: 0 14px 28px rgba(29, 56, 79, 0.08);
}

.metric-card--accent {
  background: linear-gradient(160deg, rgba(255, 244, 232, 0.98), rgba(255, 255, 255, 0.82));
  border-color: rgba(220, 122, 48, 0.18);
}

.metric-label {
  color: var(--muted);
  font-size: 13px;
  letter-spacing: 0.04em;
}

.metric-value {
  font-size: 19px;
  line-height: 1.35;
  word-break: break-word;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(320px, 0.95fr);
  gap: 22px;
  margin-top: 22px;
  align-items: start;
}

.main-column,
.dual-grid {
  display: grid;
  gap: 22px;
}

.dual-grid {
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
}

.result-column {
  position: sticky;
  top: 22px;
  display: grid;
  gap: 10px;
}

.column-label {
  margin: 0;
  padding-left: 4px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted);
}

@media (max-width: 1260px) {
  .hero-card,
  .content-grid,
  .dual-grid,
  .hero-metrics {
    grid-template-columns: 1fr;
  }

  .result-column {
    position: static;
  }
}

@media (max-width: 680px) {
  .workspace {
    width: min(100vw - 24px, 100%);
    padding-top: 20px;
    padding-bottom: 24px;
  }

  .hero-card {
    padding: 20px;
    border-radius: 28px;
  }

  .hero-title {
    max-width: none;
  }

  .hero-flow-card {
    padding: 16px;
    border-radius: 24px;
  }
}
</style>
