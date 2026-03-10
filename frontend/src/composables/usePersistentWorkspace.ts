import { watch, shallowRef } from 'vue'

import {
  createDefaultBatchForm,
  createDefaultCacheForm,
  createDefaultDownloadAdvancedForm,
  createDefaultDownloadForm,
} from '@/lib/defaults'
import type { StatusKind } from '@/types/api'
import type {
  ApiMode,
  BatchForm,
  CacheForm,
  DownloadAdvancedForm,
  DownloadForm,
  DownloadMode,
  WorkspaceSettingsSnapshot,
} from '@/types/forms'

const STORAGE_KEY = 'bilibili_media_webui_settings_v2'
const LEGACY_STORAGE_KEY = 'bilibili_media_webui_settings_v1'

interface WorkspaceForms {
  cacheForm: CacheForm
  downloadForm: DownloadForm
  batchForm: BatchForm
}

interface WorkspaceDefaults {
  defaultCachePath: string
  defaultBbdown: string
}

type Notify = (text: string, kind?: StatusKind) => void

const downloadModeOptions: DownloadMode[] = ['', 'video-only', 'audio-only', 'danmaku-only', 'sub-only', 'cover-only']
const apiModeOptions: ApiMode[] = ['', 'tv', 'app', 'intl']

export function usePersistentWorkspace(forms: WorkspaceForms, notify: Notify) {
  const hydrated = shallowRef(false)

  function createSnapshot(): WorkspaceSettingsSnapshot {
    return {
      cache: { ...forms.cacheForm },
      download: {
        ...forms.downloadForm,
        advanced: { ...forms.downloadForm.advanced },
      },
      batch: { ...forms.batchForm },
    }
  }

  function applyCacheForm(target: CacheForm, source: Partial<CacheForm> | undefined) {
    if (!source) {
      return
    }
    Object.assign(target, source)
  }

  function applyAdvancedForm(target: DownloadAdvancedForm, source: Partial<DownloadAdvancedForm> | undefined) {
    if (!source) {
      return
    }
    Object.assign(target, source)
  }

  function applyDownloadForm(target: DownloadForm, source: Partial<DownloadForm> | undefined) {
    if (!source) {
      return
    }
    const { advanced, ...rest } = source
    Object.assign(target, rest)
    applyAdvancedForm(target.advanced, advanced)
  }

  function applyBatchForm(target: BatchForm, source: Partial<BatchForm> | undefined) {
    if (!source) {
      return
    }
    Object.assign(target, source)
  }

  function buildDefaults(defaults: WorkspaceDefaults): WorkspaceSettingsSnapshot {
    return {
      cache: createDefaultCacheForm(defaults.defaultCachePath),
      download: createDefaultDownloadForm(defaults.defaultBbdown),
      batch: createDefaultBatchForm(),
    }
  }

  function coerceDownloadMode(value: unknown): DownloadMode {
    const normalized = String(value ?? '')
    return downloadModeOptions.includes(normalized as DownloadMode) ? (normalized as DownloadMode) : ''
  }

  function coerceApiMode(value: unknown): ApiMode {
    const normalized = String(value ?? '')
    return apiModeOptions.includes(normalized as ApiMode) ? (normalized as ApiMode) : ''
  }

  function migrateLegacy(raw: Record<string, unknown>, defaults: WorkspaceDefaults): WorkspaceSettingsSnapshot {
    const snapshot = buildDefaults(defaults)
    snapshot.cache = {
      inputPath: String(raw.cache_input_path ?? snapshot.cache.inputPath),
      output: String(raw.cache_output ?? snapshot.cache.output),
      ffmpeg: String(raw.cache_ffmpeg ?? snapshot.cache.ffmpeg),
      ffprobe: String(raw.cache_ffprobe ?? snapshot.cache.ffprobe),
      force: Boolean(raw.cache_force),
      dryRun: Boolean(raw.cache_dry_run),
    }

    snapshot.download = {
      videoUrl: String(raw.video_url ?? snapshot.download.videoUrl),
      output: String(raw.download_output ?? snapshot.download.output),
      bbdownPath: String(raw.bbdown_path ?? snapshot.download.bbdownPath),
      qualitySelect: String(raw.quality_select ?? snapshot.download.qualitySelect),
      qualityCustom: String(raw.quality_custom ?? snapshot.download.qualityCustom),
      pageSpec: String(raw.page_spec ?? snapshot.download.pageSpec),
      showAllPages: Boolean(raw.show_all_pages),
      advancedOpen: Boolean(raw.advanced_open),
      advanced: {
        ...createDefaultDownloadAdvancedForm(),
        downloadMode: coerceDownloadMode(raw.download_mode),
        apiMode: coerceApiMode(raw.api_mode),
        encodingPriority: String(raw.encoding_priority ?? ''),
        language: String(raw.language ?? ''),
        userAgent: String(raw.user_agent ?? ''),
        cookieText: String(raw.cookie_text ?? ''),
        accessToken: String(raw.access_token ?? ''),
        downloadDanmaku: Boolean(raw.download_danmaku),
        skipSubtitle: Boolean(raw.skip_subtitle),
        skipCover: Boolean(raw.skip_cover),
        useAria2c: Boolean(raw.use_aria2c),
        useMp4box: Boolean(raw.use_mp4box),
        skipMux: Boolean(raw.skip_mux),
        hideStreams: Boolean(raw.hide_streams),
        debugMode: Boolean(raw.debug_mode),
        downloadAiSubtitle: Boolean(raw.download_ai_subtitle),
        videoAscending: Boolean(raw.video_ascending),
        audioAscending: Boolean(raw.audio_ascending),
        allowPcdn: Boolean(raw.allow_pcdn),
        saveArchivesToFile: Boolean(raw.save_archives_to_file),
        ffmpegPath: String(raw.ffmpeg_path ?? ''),
        mp4boxPath: String(raw.mp4box_path ?? ''),
        aria2cPath: String(raw.aria2c_path ?? ''),
        aria2cArgs: String(raw.aria2c_args ?? ''),
        delayPerPage: String(raw.delay_per_page ?? ''),
        filePattern: String(raw.file_pattern ?? ''),
        multiFilePattern: String(raw.multi_file_pattern ?? ''),
        workDirOverride: String(raw.work_dir_override ?? ''),
        uposHost: String(raw.upos_host ?? ''),
        biliHost: String(raw.bili_host ?? ''),
        epHost: String(raw.ep_host ?? ''),
        area: String(raw.area ?? ''),
        configFile: String(raw.config_file ?? ''),
        extraArgs: String(raw.extra_args ?? ''),
      },
    }

    snapshot.batch = {
      urlsText: String(raw.batch_urls ?? ''),
      continueOnError: raw.batch_continue_on_error === undefined ? true : Boolean(raw.batch_continue_on_error),
    }

    return snapshot
  }

  function hydrate(defaults: WorkspaceDefaults) {
    const nextSnapshot = buildDefaults(defaults)

    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      try {
        const parsed = JSON.parse(raw) as Partial<WorkspaceSettingsSnapshot>
        applyCacheForm(nextSnapshot.cache, parsed.cache)
        applyDownloadForm(nextSnapshot.download, parsed.download)
        applyBatchForm(nextSnapshot.batch, parsed.batch)
      } catch {
        localStorage.removeItem(STORAGE_KEY)
      }
    } else {
      const legacyRaw = localStorage.getItem(LEGACY_STORAGE_KEY)
      if (legacyRaw) {
        try {
          const migrated = migrateLegacy(JSON.parse(legacyRaw) as Record<string, unknown>, defaults)
          applyCacheForm(nextSnapshot.cache, migrated.cache)
          applyDownloadForm(nextSnapshot.download, migrated.download)
          applyBatchForm(nextSnapshot.batch, migrated.batch)
        } catch {
          localStorage.removeItem(LEGACY_STORAGE_KEY)
        }
      }
    }

    applyCacheForm(forms.cacheForm, nextSnapshot.cache)
    applyDownloadForm(forms.downloadForm, nextSnapshot.download)
    applyBatchForm(forms.batchForm, nextSnapshot.batch)
    hydrated.value = true
  }

  function save(showToast = false) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(createSnapshot()))
    if (showToast) {
      notify('设置已保存到本地浏览器。', 'ok')
    }
  }

  function clear() {
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem(LEGACY_STORAGE_KEY)
    notify('已清除浏览器中保存的设置。', 'warn')
  }

  watch(
    () => createSnapshot(),
    (snapshot) => {
      if (!hydrated.value) {
        return
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot))
    },
    { deep: true },
  )

  return {
    hydrate,
    save,
    clear,
  }
}
