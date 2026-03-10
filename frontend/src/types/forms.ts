export interface CacheForm {
  inputPath: string
  output: string
  ffmpeg: string
  ffprobe: string
  force: boolean
  dryRun: boolean
}

export type DownloadMode = '' | 'video-only' | 'audio-only' | 'danmaku-only' | 'sub-only' | 'cover-only'
export type ApiMode = '' | 'tv' | 'app' | 'intl'

export interface DownloadAdvancedForm {
  downloadMode: DownloadMode
  apiMode: ApiMode
  encodingPriority: string
  language: string
  userAgent: string
  cookieText: string
  accessToken: string
  downloadDanmaku: boolean
  skipSubtitle: boolean
  skipCover: boolean
  useAria2c: boolean
  useMp4box: boolean
  skipMux: boolean
  hideStreams: boolean
  debugMode: boolean
  downloadAiSubtitle: boolean
  videoAscending: boolean
  audioAscending: boolean
  allowPcdn: boolean
  saveArchivesToFile: boolean
  ffmpegPath: string
  mp4boxPath: string
  aria2cPath: string
  aria2cArgs: string
  delayPerPage: string
  filePattern: string
  multiFilePattern: string
  workDirOverride: string
  uposHost: string
  biliHost: string
  epHost: string
  area: string
  configFile: string
  extraArgs: string
}

export interface DownloadForm {
  videoUrl: string
  output: string
  bbdownPath: string
  qualitySelect: string
  qualityCustom: string
  pageSpec: string
  showAllPages: boolean
  advancedOpen: boolean
  advanced: DownloadAdvancedForm
}

export interface BatchForm {
  urlsText: string
  continueOnError: boolean
}

export interface WorkspaceSettingsSnapshot {
  cache: CacheForm
  download: DownloadForm
  batch: BatchForm
}
