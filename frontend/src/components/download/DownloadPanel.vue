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
  <v-card class="h-100 rounded-lg top-accent-line panel-card" flat>
    <v-card-text>
      <div class="d-flex justify-space-between align-start mb-4">
        <div>
          <div class="text-overline text-medium-emphasis">模式二</div>
          <div class="text-h6 font-weight-bold">视频链接下载</div>
          <div class="text-body-2 text-medium-emphasis mt-1">围绕 BBDown 的单链接工作流，覆盖账号状态、清晰度、分 P 与高级参数。</div>
        </div>
        <v-chip size="small" color="primary" variant="tonal" class="font-weight-bold">BBDown 工作流</v-chip>
      </div>

      <LoginStatusCard
        :login-status="props.loginStatus"
        class="mb-4"
        @refresh="emit('refreshLogin')"
        @login-web="emit('loginWeb')"
        @login-tv="emit('loginTv')"
        @clear="emit('clearLogin')"
      />

      <ToolStatusPanel :detection="props.toolDetection" class="mb-6" @detect="emit('detectTools')" />

      <v-form @submit.prevent="emit('runDownload')">
        <div class="text-subtitle-2 font-weight-bold mb-3 text-primary">基础参数</div>

        <v-text-field
          v-model="form.videoUrl"
          label="B 站视频链接"
          placeholder="例如：https://www.bilibili.com/video/BV..."
          required
          variant="outlined"
          density="compact"
          hint="支持直接粘贴分享文本、纯链接或 BV / av / ep / ss 编号，失焦时会自动识别。"
          persistent-hint
          class="mb-3"
          @blur="normalizeVideoUrl"
          @paste="handlePaste"
        ></v-text-field>

        <v-row dense class="mb-1">
          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.output"
              label="下载目录"
              placeholder="留空则下载到当前仓库目录"
              variant="outlined"
              density="compact"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.bbdownPath"
              label="BBDown 路径"
              variant="outlined"
              density="compact"
            ></v-text-field>
          </v-col>
        </v-row>

        <v-row dense class="mb-1">
          <v-col cols="12" md="6">
            <v-select
              v-model="form.qualitySelect"
              :items="qualitySelectOptions"
              label="清晰度"
              variant="outlined"
              density="compact"
            ></v-select>
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.qualityCustom"
              label="自定义清晰度文本"
              placeholder="例如：1080P 高码率"
              variant="outlined"
              density="compact"
            ></v-text-field>
          </v-col>
        </v-row>

        <v-text-field
          v-model="form.pageSpec"
          label="分 P / 剧集范围"
          placeholder="留空=默认；全集填 ALL；也支持 1-5、1,3,7、LAST"
          variant="outlined"
          density="compact"
          hint="适用于多 P、合集、番剧、课程等，支持 ALL、LAST、1-5、1,3,7。"
          persistent-hint
          class="mb-2"
        ></v-text-field>

        <v-switch
          v-model="form.showAllPages"
          label="获取信息时显示全部分 P / 剧集列表"
          color="primary"
          density="compact"
          class="mb-3"
          hide-details
        ></v-switch>

        <PagePickerPanel v-model="form.pageSpec" :items="props.pageItems" :meta="props.pageMeta" class="mb-4" @refresh="emit('fetchInfo')" />

        <div class="mb-4">
          <v-btn variant="text" size="small" color="medium-emphasis" @click="toggleAdvancedMode">
            <v-icon start>{{ form.advancedOpen ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
            {{ form.advancedOpen ? '收起高级选项' : '展开高级选项' }}
          </v-btn>
        </div>

        <v-expand-transition>
          <div v-show="form.advancedOpen">
            <v-card variant="outlined" class="pa-4 mb-4 rounded-lg advanced-panel">
              <div class="text-subtitle-2 font-weight-bold mb-3 text-primary">高级下载选项</div>

              <v-row dense>
                <v-col cols="12" sm="6">
                  <v-select
                    v-model="form.advanced.downloadMode"
                    label="下载模式"
                    :items="[
                      {title: '默认（正常下载）', value: ''},
                      {title: '仅下载视频', value: 'video-only'},
                      {title: '仅下载音频', value: 'audio-only'},
                      {title: '仅下载弹幕', value: 'danmaku-only'},
                      {title: '仅下载字幕', value: 'sub-only'},
                      {title: '仅下载封面', value: 'cover-only'}
                    ]"
                    variant="outlined"
                    density="compact"
                  ></v-select>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-select
                    v-model="form.advanced.apiMode"
                    label="解析模式"
                    :items="[
                      {title: '默认', value: ''},
                      {title: 'TV 端', value: 'tv'},
                      {title: 'APP 端', value: 'app'},
                      {title: '国际版', value: 'intl'}
                    ]"
                    variant="outlined"
                    density="compact"
                  ></v-select>
                </v-col>
              </v-row>

              <v-row dense>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.encodingPriority" label="视频编码优先级" placeholder="例如：hevc,av1,avc" variant="outlined" density="compact"></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.language" label="音频语言" placeholder="例如：chi、jpn" variant="outlined" density="compact"></v-text-field>
                </v-col>
              </v-row>

              <v-row dense>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.userAgent" label="User-Agent" placeholder="留空则使用 BBDown 默认策略" variant="outlined" density="compact"></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.cookieText" label="Cookie / SESSDATA" placeholder="留空则不额外传 cookie" variant="outlined" density="compact"></v-text-field>
                </v-col>
              </v-row>

              <v-row dense>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.accessToken" label="Access Token" placeholder="TV / APP 接口需要时可填写" variant="outlined" density="compact"></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.ffmpegPath" label="ffmpeg 路径" placeholder="留空则走系统 PATH" variant="outlined" density="compact"></v-text-field>
                </v-col>
              </v-row>

              <v-row dense>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.mp4boxPath" label="MP4Box 路径" placeholder="使用 MP4Box 时可指定路径" variant="outlined" density="compact"></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.aria2cPath" label="aria2c 路径" placeholder="留空则走系统 PATH" variant="outlined" density="compact"></v-text-field>
                </v-col>
              </v-row>

              <v-row dense>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.aria2cArgs" label="aria2c 附加参数" placeholder="例如：--max-concurrent-downloads=8" variant="outlined" density="compact"></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.delayPerPage" label="合集每 P 间隔秒数" placeholder="例如：2" variant="outlined" density="compact"></v-text-field>
                </v-col>
              </v-row>

              <v-row dense>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.filePattern" label="单 P 文件名模板" placeholder="例如：<videoTitle>-<dfn>" variant="outlined" density="compact"></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.multiFilePattern" label="多 P 文件名模板" placeholder="例如：<videoTitle>/[P<pageNumberWithZero>]<pageTitle>" variant="outlined" density="compact"></v-text-field>
                </v-col>
              </v-row>

              <v-row dense>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.workDirOverride" label="工作目录覆盖" placeholder="例如：D:\Downloads" variant="outlined" density="compact"></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.uposHost" label="UPOS Host" placeholder="例如：upos-sz-mirrorcos.bilivideo.com" variant="outlined" density="compact"></v-text-field>
                </v-col>
              </v-row>

              <v-row dense>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.biliHost" label="BiliPlus Host" placeholder="例如：https://www.biliplus.com" variant="outlined" density="compact"></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.epHost" label="EP Host" placeholder="代理番剧 season 接口时可填写" variant="outlined" density="compact"></v-text-field>
                </v-col>
              </v-row>

              <v-row dense>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.area" label="Area" placeholder="hk / tw / th" variant="outlined" density="compact"></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field v-model="form.advanced.configFile" label="配置文件" placeholder="例如：BBDown.config" variant="outlined" density="compact"></v-text-field>
                </v-col>
              </v-row>

              <v-text-field v-model="form.advanced.extraArgs" label="额外 BBDown 参数" placeholder='例如：--work-dir "D:\Downloads"' variant="outlined" density="compact" class="mb-2"></v-text-field>

              <div class="d-flex flex-wrap gap-2">
                <v-checkbox v-model="form.advanced.downloadDanmaku" label="同时下载弹幕" density="compact" hide-details></v-checkbox>
                <v-checkbox v-model="form.advanced.skipSubtitle" label="跳过字幕" density="compact" hide-details></v-checkbox>
                <v-checkbox v-model="form.advanced.skipCover" label="跳过封面" density="compact" hide-details></v-checkbox>
                <v-checkbox v-model="form.advanced.useAria2c" label="使用 aria2c" density="compact" hide-details></v-checkbox>
                <v-checkbox v-model="form.advanced.useMp4box" label="使用 MP4Box 混流" density="compact" hide-details></v-checkbox>
                <v-checkbox v-model="form.advanced.skipMux" label="跳过混流" density="compact" hide-details></v-checkbox>
                <v-checkbox v-model="form.advanced.hideStreams" label="隐藏可用流信息" density="compact" hide-details></v-checkbox>
                <v-checkbox v-model="form.advanced.debugMode" label="输出调试日志" density="compact" hide-details></v-checkbox>
                <v-checkbox v-model="form.advanced.downloadAiSubtitle" label="下载 AI 字幕" density="compact" hide-details></v-checkbox>
                <v-checkbox v-model="form.advanced.videoAscending" label="视频升序" density="compact" hide-details></v-checkbox>
                <v-checkbox v-model="form.advanced.audioAscending" label="音频升序" density="compact" hide-details></v-checkbox>
                <v-checkbox v-model="form.advanced.allowPcdn" label="允许 PCDN" density="compact" hide-details></v-checkbox>
                <v-checkbox v-model="form.advanced.saveArchivesToFile" label="记录已下载视频" density="compact" hide-details></v-checkbox>
              </div>
            </v-card>
          </div>
        </v-expand-transition>

        <div class="d-flex flex-wrap gap-2">
          <v-btn color="primary" type="submit" :loading="props.busy" :disabled="props.busy" elevation="1">开始下载</v-btn>
          <v-btn variant="outlined" :loading="props.busy" :disabled="props.busy" @click="emit('fetchInfo')">获取画质/分P</v-btn>
          <v-btn variant="text" @click="emit('fillExample')">填入示例</v-btn>
        </div>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.panel-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  background: rgba(var(--v-theme-surface), 0.8);
  backdrop-filter: blur(10px);
}

.top-accent-line {
  position: relative;
}

.top-accent-line::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, rgba(220, 122, 48, 0.6), rgba(var(--v-theme-primary), 0.8));
}

.advanced-panel {
  background: rgba(var(--v-theme-surface-variant), 0.3);
}

.gap-2 {
  gap: 8px;
}
</style>
