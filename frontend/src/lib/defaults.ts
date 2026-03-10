import type { BootstrapResponse, LoginStatus, OperationResult } from '@/types/api'
import type { BatchForm, CacheForm, DownloadAdvancedForm, DownloadForm } from '@/types/forms'

export const DEFAULT_QUALITY_OPTIONS = [
  '自动（最高可用）',
  '8K 超高清',
  '杜比视界',
  'HDR 真彩',
  '4K 超清',
  '1080P 高码率',
  '1080P 高清',
  '720P 高清',
  '480P 清晰',
  '360P 流畅',
]

export const FALLBACK_BOOTSTRAP: BootstrapResponse = {
  default_cache_path: 'C:\\Users\\曹乐\\Videos\\bilibili',
  default_bbdown: 'BBDown',
  quality_options: DEFAULT_QUALITY_OPTIONS,
  server_url: 'http://127.0.0.1:8767',
  frontend_dist_ready: false,
}

export function createDefaultCacheForm(defaultCachePath = FALLBACK_BOOTSTRAP.default_cache_path): CacheForm {
  return {
    inputPath: defaultCachePath,
    output: '',
    ffmpeg: 'ffmpeg',
    ffprobe: '',
    force: false,
    dryRun: false,
  }
}

export function createDefaultDownloadAdvancedForm(): DownloadAdvancedForm {
  return {
    downloadMode: '',
    apiMode: '',
    encodingPriority: '',
    language: '',
    userAgent: '',
    cookieText: '',
    accessToken: '',
    downloadDanmaku: false,
    skipSubtitle: false,
    skipCover: false,
    useAria2c: false,
    useMp4box: false,
    skipMux: false,
    hideStreams: false,
    debugMode: false,
    downloadAiSubtitle: false,
    videoAscending: false,
    audioAscending: false,
    allowPcdn: false,
    saveArchivesToFile: false,
    ffmpegPath: '',
    mp4boxPath: '',
    aria2cPath: '',
    aria2cArgs: '',
    delayPerPage: '',
    filePattern: '',
    multiFilePattern: '',
    workDirOverride: '',
    uposHost: '',
    biliHost: '',
    epHost: '',
    area: '',
    configFile: '',
    extraArgs: '',
  }
}

export function createDefaultDownloadForm(defaultBbdown = FALLBACK_BOOTSTRAP.default_bbdown): DownloadForm {
  return {
    videoUrl: '',
    output: '',
    bbdownPath: defaultBbdown,
    qualitySelect: DEFAULT_QUALITY_OPTIONS[0],
    qualityCustom: '',
    pageSpec: '',
    showAllPages: false,
    advancedOpen: false,
    advanced: createDefaultDownloadAdvancedForm(),
  }
}

export function createDefaultBatchForm(): BatchForm {
  return {
    urlsText: '',
    continueOnError: true,
  }
}

export function createEmptyLoginStatus(): LoginStatus {
  return {
    logged_in: false,
    login_type: '',
    account_name: '',
    uid: '',
    expires_at: '',
    message: '正在获取登录状态...',
  }
}

export function createEmptyResult(): OperationResult {
  return {
    command: '-',
    returncode: '-',
    finished_at: '-',
    stdout: '',
    stderr: '',
  }
}

export function getCacheExample(defaultCachePath: string): CacheForm {
  return {
    ...createDefaultCacheForm(defaultCachePath),
    force: true,
  }
}

export function getDownloadExample(defaultBbdown: string): DownloadForm {
  return {
    ...createDefaultDownloadForm(defaultBbdown),
    videoUrl: 'https://www.bilibili.com/video/BV1494y1C72o',
    qualitySelect: '1080P 高清',
    pageSpec: 'ALL',
    showAllPages: true,
    advancedOpen: true,
    advanced: {
      ...createDefaultDownloadAdvancedForm(),
      downloadMode: 'sub-only',
    },
  }
}

export function getBatchExample(): BatchForm {
  return {
    urlsText: [
      'https://www.bilibili.com/video/BV1494y1C72o',
      'BV1494y1C72o',
      '【示例分享文本】https://www.bilibili.com/video/BV1494y1C72o?vd_source=330f8fe25b57ed8ec864c0f881472669',
    ].join('\n'),
    continueOnError: true,
  }
}

export function mergeQualityOptions(base: string[], extra: string[]): string[] {
  const values = [...base, ...extra].filter(Boolean)
  const seen = new Set<string>()
  const merged: string[] = []
  for (const value of values) {
    if (seen.has(value)) {
      continue
    }
    seen.add(value)
    merged.push(value)
  }
  return merged
}
