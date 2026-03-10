<script setup lang="ts">
import { computed } from 'vue'

import { mergeQualityOptions } from '@/lib/defaults'
import { extractBilibiliTarget } from '@/lib/video'
import type { LoginStatus, PageItem, PagePickerMeta, ToolDetectResponse } from '@/types/api'
import type { DownloadForm } from '@/types/forms'

import LoginStatusCard from './LoginStatusCard.vue'
import PagePickerPanel from './PagePickerPanel.vue'
import ToolStatusPanel from './ToolStatusPanel.vue'

const props = defineProps<{
  busy: boolean
  qualityOptions: string[]
  loginStatus: LoginStatus
  toolDetection: ToolDetectResponse | null
  pageItems: PageItem[]
  pageMeta: PagePickerMeta
}>()

const form = defineModel<DownloadForm>({ required: true })

const emit = defineEmits<{
  fetchInfo: []
  runDownload: []
  fillExample: []
  refreshLogin: []
  loginWeb: []
  loginTv: []
  clearLogin: []
  detectTools: []
}>()

const qualitySelectOptions = computed(() => {
  const current = form.value.qualitySelect ? [form.value.qualitySelect] : []
  return mergeQualityOptions(props.qualityOptions, current)
})

function normalizeVideoUrl() {
  const normalized = extractBilibiliTarget(form.value.videoUrl)
  if (normalized && normalized !== form.value.videoUrl.trim()) {
    form.value.videoUrl = normalized
  }
}

function handlePaste() {
  window.setTimeout(() => {
    normalizeVideoUrl()
  }, 0)
}

function toggleAdvancedMode() {
  form.value.advancedOpen = !form.value.advancedOpen
}
</script>

<template>
  <section class="panel-card">
    <div class="panel-head">
      <div>
        <p class="eyebrow">模式二</p>
        <h2 class="title">视频链接下载</h2>
        <p class="summary">围绕 BBDown 的单链接工作流，覆盖账号状态、清晰度、分 P 与高级参数。</p>
      </div>
      <span class="tag">BBDown 工作流</span>
    </div>

    <LoginStatusCard
      :login-status="props.loginStatus"
      @refresh="emit('refreshLogin')"
      @login-web="emit('loginWeb')"
      @login-tv="emit('loginTv')"
      @clear="emit('clearLogin')"
    />

    <ToolStatusPanel :detection="props.toolDetection" @detect="emit('detectTools')" />

    <form class="panel-form" @submit.prevent="emit('runDownload')">
      <p class="section-label">基础参数</p>

      <div class="field">
        <label class="field-label" for="video-url">B 站视频链接</label>
        <input
          id="video-url"
          v-model="form.videoUrl"
          class="field-input"
          type="text"
          placeholder="例如：https://www.bilibili.com/video/BV..."
          required
          @blur="normalizeVideoUrl"
          @paste="handlePaste"
        />
        <p class="field-help">支持直接粘贴分享文本、纯链接或 BV / av / ep / ss 编号，失焦时会自动识别。</p>
      </div>

      <div class="field-grid">
        <div class="field">
          <label class="field-label" for="download-output">下载目录</label>
          <input id="download-output" v-model="form.output" class="field-input" type="text" placeholder="留空则下载到当前仓库目录" />
        </div>

        <div class="field">
          <label class="field-label" for="bbdown-path">BBDown 路径</label>
          <input id="bbdown-path" v-model="form.bbdownPath" class="field-input" type="text" />
        </div>
      </div>

      <div class="field-grid">
        <div class="field">
          <label class="field-label" for="quality-select">清晰度</label>
          <select id="quality-select" v-model="form.qualitySelect" class="field-input">
            <option v-for="option in qualitySelectOptions" :key="option" :value="option">{{ option }}</option>
          </select>
        </div>

        <div class="field">
          <label class="field-label" for="quality-custom">自定义清晰度文本</label>
          <input id="quality-custom" v-model="form.qualityCustom" class="field-input" type="text" placeholder="例如：1080P 高码率" />
        </div>
      </div>

      <div class="field">
        <label class="field-label" for="page-spec">分 P / 剧集范围</label>
        <input id="page-spec" v-model="form.pageSpec" class="field-input" type="text" placeholder="留空=默认；全集填 ALL；也支持 1-5、1,3,7、LAST" />
        <p class="field-help">适用于多 P、合集、番剧、课程等，支持 ALL、LAST、1-5、1,3,7。</p>
      </div>

      <label class="toggle-item">
        <input v-model="form.showAllPages" type="checkbox" />
        <span>获取信息时显示全部分 P / 剧集列表</span>
      </label>

      <PagePickerPanel v-model="form.pageSpec" :items="props.pageItems" :meta="props.pageMeta" @refresh="emit('fetchInfo')" />

      <div class="actions">
        <button class="secondary" type="button" @click="toggleAdvancedMode">
          {{ form.advancedOpen ? '切换到简约模式' : '显示更多功能' }}
        </button>
      </div>

      <section v-show="form.advancedOpen" class="advanced-panel">
        <p class="section-label section-label--inside">增强能力</p>
        <h3 class="advanced-title">高级下载选项</h3>

        <div class="field-grid">
          <div class="field">
            <label class="field-label" for="download-mode">下载模式</label>
            <select id="download-mode" v-model="form.advanced.downloadMode" class="field-input">
              <option value="">默认（正常下载）</option>
              <option value="video-only">仅下载视频</option>
              <option value="audio-only">仅下载音频</option>
              <option value="danmaku-only">仅下载弹幕</option>
              <option value="sub-only">仅下载字幕</option>
              <option value="cover-only">仅下载封面</option>
            </select>
          </div>

          <div class="field">
            <label class="field-label" for="api-mode">解析模式</label>
            <select id="api-mode" v-model="form.advanced.apiMode" class="field-input">
              <option value="">默认</option>
              <option value="tv">TV 端</option>
              <option value="app">APP 端</option>
              <option value="intl">国际版</option>
            </select>
          </div>
        </div>

        <div class="field-grid">
          <div class="field">
            <label class="field-label" for="encoding-priority">视频编码优先级</label>
            <input id="encoding-priority" v-model="form.advanced.encodingPriority" class="field-input" type="text" placeholder="例如：hevc,av1,avc" />
          </div>

          <div class="field">
            <label class="field-label" for="language">音频语言</label>
            <input id="language" v-model="form.advanced.language" class="field-input" type="text" placeholder="例如：chi、jpn" />
          </div>
        </div>

        <div class="field-grid">
          <div class="field">
            <label class="field-label" for="user-agent">User-Agent</label>
            <input id="user-agent" v-model="form.advanced.userAgent" class="field-input" type="text" placeholder="留空则使用 BBDown 默认策略" />
          </div>

          <div class="field">
            <label class="field-label" for="cookie-text">Cookie / SESSDATA</label>
            <input id="cookie-text" v-model="form.advanced.cookieText" class="field-input" type="text" placeholder="留空则不额外传 cookie" />
          </div>
        </div>

        <div class="field-grid">
          <div class="field">
            <label class="field-label" for="access-token">Access Token</label>
            <input id="access-token" v-model="form.advanced.accessToken" class="field-input" type="text" placeholder="TV / APP 接口需要时可填写" />
          </div>

          <div class="field">
            <label class="field-label" for="ffmpeg-path">ffmpeg 路径</label>
            <input id="ffmpeg-path" v-model="form.advanced.ffmpegPath" class="field-input" type="text" placeholder="留空则走系统 PATH" />
          </div>
        </div>

        <div class="field-grid">
          <div class="field">
            <label class="field-label" for="mp4box-path">MP4Box 路径</label>
            <input id="mp4box-path" v-model="form.advanced.mp4boxPath" class="field-input" type="text" placeholder="使用 MP4Box 时可指定路径" />
          </div>

          <div class="field">
            <label class="field-label" for="aria2c-path">aria2c 路径</label>
            <input id="aria2c-path" v-model="form.advanced.aria2cPath" class="field-input" type="text" placeholder="留空则走系统 PATH" />
          </div>
        </div>

        <div class="field-grid">
          <div class="field">
            <label class="field-label" for="aria2c-args">aria2c 附加参数</label>
            <input id="aria2c-args" v-model="form.advanced.aria2cArgs" class="field-input" type="text" placeholder="例如：--max-concurrent-downloads=8" />
          </div>

          <div class="field">
            <label class="field-label" for="delay-per-page">合集每 P 间隔秒数</label>
            <input id="delay-per-page" v-model="form.advanced.delayPerPage" class="field-input" type="text" placeholder="例如：2" />
          </div>
        </div>

        <div class="field-grid">
          <div class="field">
            <label class="field-label" for="file-pattern">单 P 文件名模板</label>
            <input id="file-pattern" v-model="form.advanced.filePattern" class="field-input" type="text" placeholder="例如：&lt;videoTitle&gt;-&lt;dfn&gt;" />
          </div>

          <div class="field">
            <label class="field-label" for="multi-file-pattern">多 P 文件名模板</label>
            <input
              id="multi-file-pattern"
              v-model="form.advanced.multiFilePattern"
              class="field-input"
              type="text"
              placeholder="例如：&lt;videoTitle&gt;/[P&lt;pageNumberWithZero&gt;]&lt;pageTitle&gt;"
            />
          </div>
        </div>

        <div class="field-grid">
          <div class="field">
            <label class="field-label" for="work-dir-override">工作目录覆盖</label>
            <input id="work-dir-override" v-model="form.advanced.workDirOverride" class="field-input" type="text" placeholder="例如：D:\\Downloads" />
          </div>

          <div class="field">
            <label class="field-label" for="upos-host">UPOS Host</label>
            <input id="upos-host" v-model="form.advanced.uposHost" class="field-input" type="text" placeholder="例如：upos-sz-mirrorcos.bilivideo.com" />
          </div>
        </div>

        <div class="field-grid">
          <div class="field">
            <label class="field-label" for="bili-host">BiliPlus Host</label>
            <input id="bili-host" v-model="form.advanced.biliHost" class="field-input" type="text" placeholder="例如：https://www.biliplus.com" />
          </div>

          <div class="field">
            <label class="field-label" for="ep-host">EP Host</label>
            <input id="ep-host" v-model="form.advanced.epHost" class="field-input" type="text" placeholder="代理番剧 season 接口时可填写" />
          </div>
        </div>

        <div class="field-grid">
          <div class="field">
            <label class="field-label" for="area">Area</label>
            <input id="area" v-model="form.advanced.area" class="field-input" type="text" placeholder="hk / tw / th" />
          </div>

          <div class="field">
            <label class="field-label" for="config-file">配置文件</label>
            <input id="config-file" v-model="form.advanced.configFile" class="field-input" type="text" placeholder="例如：BBDown.config" />
          </div>
        </div>

        <div class="field">
          <label class="field-label" for="extra-args">额外 BBDown 参数</label>
          <input id="extra-args" v-model="form.advanced.extraArgs" class="field-input" type="text" placeholder='例如：--work-dir "D:\\Downloads"' />
        </div>

        <div class="toggle-grid">
          <label class="toggle-item"><input v-model="form.advanced.downloadDanmaku" type="checkbox" /><span>同时下载弹幕</span></label>
          <label class="toggle-item"><input v-model="form.advanced.skipSubtitle" type="checkbox" /><span>跳过字幕</span></label>
          <label class="toggle-item"><input v-model="form.advanced.skipCover" type="checkbox" /><span>跳过封面</span></label>
          <label class="toggle-item"><input v-model="form.advanced.useAria2c" type="checkbox" /><span>使用 aria2c</span></label>
          <label class="toggle-item"><input v-model="form.advanced.useMp4box" type="checkbox" /><span>使用 MP4Box 混流</span></label>
          <label class="toggle-item"><input v-model="form.advanced.skipMux" type="checkbox" /><span>跳过混流</span></label>
          <label class="toggle-item"><input v-model="form.advanced.hideStreams" type="checkbox" /><span>隐藏可用流信息</span></label>
          <label class="toggle-item"><input v-model="form.advanced.debugMode" type="checkbox" /><span>输出调试日志</span></label>
          <label class="toggle-item"><input v-model="form.advanced.downloadAiSubtitle" type="checkbox" /><span>下载 AI 字幕</span></label>
          <label class="toggle-item"><input v-model="form.advanced.videoAscending" type="checkbox" /><span>视频升序</span></label>
          <label class="toggle-item"><input v-model="form.advanced.audioAscending" type="checkbox" /><span>音频升序</span></label>
          <label class="toggle-item"><input v-model="form.advanced.allowPcdn" type="checkbox" /><span>允许 PCDN</span></label>
          <label class="toggle-item"><input v-model="form.advanced.saveArchivesToFile" type="checkbox" /><span>记录已下载视频</span></label>
        </div>
      </section>

      <div class="actions">
        <button class="secondary" type="button" :disabled="props.busy" @click="emit('fetchInfo')">
          {{ props.busy ? '处理中...' : '获取画质' }}
        </button>
        <button class="primary" type="submit" :disabled="props.busy">
          {{ props.busy ? '处理中...' : '开始下载' }}
        </button>
        <button class="secondary" type="button" @click="emit('fillExample')">填入示例</button>
      </div>
    </form>
  </section>
</template>

<style scoped>
.panel-card {
  display: grid;
  gap: 18px;
  padding: 24px;
  border-radius: var(--radius-xl);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(245, 250, 255, 0.82));
  border: 1px solid var(--panel-border);
  box-shadow: var(--shadow);
  backdrop-filter: blur(18px);
  position: relative;
  overflow: hidden;
  animation: floatUp 500ms ease both;
}

.panel-card::before {
  content: "";
  position: absolute;
  inset: 0 auto auto 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, var(--accent-strong), rgba(220, 122, 48, 0.35));
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted);
}

.title {
  margin: 0;
  font-size: 24px;
}

.summary {
  margin: 8px 0 0;
  max-width: 44ch;
  color: var(--muted);
  line-height: 1.7;
  font-size: 14px;
}

.tag {
  padding: 8px 14px;
  border-radius: 999px;
  background: linear-gradient(160deg, rgba(14, 91, 216, 0.1), rgba(220, 122, 48, 0.08));
  color: var(--accent-strong);
  font-size: 13px;
  font-weight: 700;
  box-shadow: inset 0 0 0 1px rgba(14, 91, 216, 0.08);
}

.panel-form,
.field-grid,
.advanced-panel {
  display: grid;
  gap: 16px;
}

.field-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.section-label {
  margin: 2px 0 0;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted);
}

.section-label--inside {
  color: var(--accent-strong);
}

.field {
  display: grid;
  gap: 8px;
}

.field-label {
  font-weight: 700;
}

.field-input {
  min-height: 50px;
  border: 1px solid rgba(34, 67, 96, 0.12);
  border-radius: 16px;
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.88);
  color: var(--text);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.field-help {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--muted);
}

.advanced-panel {
  padding: 18px;
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(242, 247, 255, 0.92), rgba(255, 249, 243, 0.82));
  border: 1px solid rgba(34, 67, 96, 0.1);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.84);
}

.advanced-title {
  margin: 0;
  font-size: 18px;
}

.toggle-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.toggle-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 42px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid rgba(34, 67, 96, 0.1);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.primary,
.secondary {
  min-height: 46px;
  padding: 0 18px;
  border-radius: 999px;
}

.primary {
  border: 0;
  background: linear-gradient(135deg, var(--accent), var(--accent-strong));
  color: #fff;
  box-shadow: 0 14px 24px rgba(14, 91, 216, 0.18);
}

.secondary {
  border: 1px solid var(--panel-border);
  background: rgba(255, 255, 255, 0.92);
  color: var(--text);
}

.primary:disabled,
.secondary:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

@media (max-width: 760px) {
  .panel-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .field-grid {
    grid-template-columns: 1fr;
  }
}
</style>
