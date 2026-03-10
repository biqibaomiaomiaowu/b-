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
  <v-container class="px-2 px-md-4 py-4 workspace-container" fluid>
    <!-- 极简风格 Hero Section -->
    <v-card flat class="mb-6 rounded-lg pa-6 hero-card">
      <v-row align="center">
        <v-col cols="12" md="7">
          <div class="text-overline mb-2 text-primary">Vue 3 + Python API</div>
          <h1 class="text-h4 text-md-h3 font-weight-bold mb-4">Bilibili 下载/转换</h1>
          <p class="text-body-1 text-medium-emphasis mb-6">
            基于 Vite 的 Vue 3 前端界面，后端专注于本地化工具检测、任务调度与下载代理。极简设计风格，专注核心功能。
          </p>
          <div class="d-flex flex-wrap gap-2">
            <v-chip color="primary" variant="flat" size="small">本地执行</v-chip>
            <v-chip variant="outlined" size="small">工具自动探测</v-chip>
            <v-chip variant="outlined" size="small">极简设计</v-chip>
          </div>
        </v-col>

        <v-col cols="12" md="5">
          <v-card variant="tonal" color="primary" class="rounded-lg pa-4">
            <v-row>
              <v-col cols="4" class="text-center">
                <div class="text-caption text-medium-emphasis">服务</div>
                <div class="text-subtitle-2 font-weight-bold">{{ serverUrl || '未连接' }}</div>
              </v-col>
              <v-col cols="4" class="text-center border-s">
                <div class="text-caption text-medium-emphasis">BBDown</div>
                <div class="text-subtitle-2 font-weight-bold text-truncate" :title="bootstrap.default_bbdown">{{ bootstrap.default_bbdown || '未设置' }}</div>
              </v-col>
              <v-col cols="4" class="text-center border-s">
                <div class="text-caption text-medium-emphasis">清晰度选项</div>
                <div class="text-subtitle-2 font-weight-bold">{{ qualityOptions.length }} 项</div>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>
    </v-card>

    <!-- 工作区主体布局 -->
    <v-row>
      <!-- 左侧操作区 -->
      <v-col cols="12" lg="8">
        <v-row>
          <!-- 缓存转换与基础下载 -->
          <v-col cols="12" md="5">
            <CacheConverterPanel v-model="cacheForm" :busy="busy" @run="runCacheConversion" @fill-example="fillCacheExample" />
          </v-col>
          <v-col cols="12" md="7">
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
          </v-col>
        </v-row>

        <!-- 批量下载区 -->
        <v-row class="mt-4">
          <v-col cols="12">
            <BatchQueuePanel v-model="batchForm" :busy="busy" @run="runBatchDownload" @fill-example="fillBatchExample" />
          </v-col>
        </v-row>
      </v-col>

      <!-- 右侧结果日志区 -->
      <v-col cols="12" lg="4">
        <div class="sticky-result">
          <div class="text-overline mb-2 ps-1">Session Log</div>
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
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.workspace-container {
  max-width: 1480px;
  margin: 0 auto;
}

.hero-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  background: rgba(var(--v-theme-surface), 0.8);
  backdrop-filter: blur(10px);
}

.gap-2 {
  gap: 8px;
}

.sticky-result {
  position: sticky;
  top: 24px;
}
</style>
