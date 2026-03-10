<script setup lang="ts">
import { computed } from 'vue'

import StatusBanner from '@/components/common/StatusBanner.vue'
import type { OperationResult, StatusKind } from '@/types/api'

const props = defineProps<{
  statusText: string
  statusKind: StatusKind
  result: OperationResult
  serverUrl: string
}>()

const emit = defineEmits<{
  copyCommand: []
  saveSettings: []
  clearSettings: []
  clearLog: []
}>()

const combinedLog = computed(() => [props.result.stdout, props.result.stderr].filter(Boolean).join('\n') || '还没有运行记录。')
</script>

<template>
  <v-card class="rounded-lg result-card d-flex flex-column h-100" flat>
    <v-card-text class="d-flex flex-column flex-grow-1 pa-4">
      <div class="d-flex flex-column flex-md-row justify-space-between align-start mb-4 gap-4">
        <div>
          <div class="text-overline text-medium-emphasis">执行结果</div>
          <div class="text-h6 font-weight-bold">运行结果</div>
          <div class="text-body-2 text-medium-emphasis mt-1">固定保留命令、退出码和完整输出，方便排错。</div>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <v-btn variant="outlined" size="small" @click="emit('copyCommand')">复制命令</v-btn>
          <v-btn variant="outlined" size="small" @click="emit('saveSettings')">保存设置</v-btn>
          <v-btn variant="outlined" size="small" @click="emit('clearSettings')">清空设置</v-btn>
          <v-btn variant="outlined" size="small" @click="emit('clearLog')">清空日志</v-btn>
        </div>
      </div>

      <div class="mb-4">
        <StatusBanner :text="statusText" :kind="statusKind" />
      </div>

      <div class="d-flex align-center gap-2 mb-3 bg-surface-variant rounded-pill px-3 py-1 align-self-start">
        <div class="terminal-dot bg-error"></div>
        <div class="terminal-dot bg-warning"></div>
        <div class="terminal-dot bg-success"></div>
        <span class="text-caption text-medium-emphasis ml-2 text-uppercase font-weight-bold tracking-widest">local session</span>
      </div>

      <v-row dense class="mb-4 flex-shrink-0">
        <v-col cols="12" sm="4">
          <v-card variant="outlined" class="pa-2 h-100 rounded bg-surface-variant">
            <div class="text-caption text-medium-emphasis mb-1">命令</div>
            <div class="text-body-2 font-weight-bold" style="word-break: break-all;">{{ result.command || '-' }}</div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="4">
          <v-card variant="outlined" class="pa-2 h-100 rounded bg-surface-variant">
            <div class="text-caption text-medium-emphasis mb-1">退出码</div>
            <div class="text-body-2 font-weight-bold">{{ result.returncode ?? '-' }}</div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="4">
          <v-card variant="outlined" class="pa-2 h-100 rounded bg-surface-variant">
            <div class="text-caption text-medium-emphasis mb-1">时间</div>
            <div class="text-body-2 font-weight-bold">{{ result.finished_at || '-' }}</div>
          </v-card>
        </v-col>
      </v-row>

      <v-card variant="flat" class="bg-black text-white rounded-lg flex-grow-1 d-flex flex-column mb-4" style="min-height: 280px;">
        <pre class="log-output pa-4 flex-grow-1">{{ combinedLog }}</pre>
      </v-card>

      <div class="text-caption text-medium-emphasis mt-auto">
        启动地址：<span class="text-high-emphasis">{{ serverUrl }}</span>
        <span class="mx-2">·</span>
        参考：
        <a href="https://github.com/nilaoda/BBDown" target="_blank" rel="noreferrer" class="text-primary text-decoration-none font-weight-bold">BBDown</a>
      </div>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.result-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  background: rgba(var(--v-theme-surface), 0.8);
  backdrop-filter: blur(10px);
}

.terminal-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.tracking-widest {
  letter-spacing: 0.1em;
}

.log-output {
  font-family: "Cascadia Code", "JetBrains Mono", Consolas, monospace;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
  overflow-y: auto;
  max-height: 600px;
}

/* 改善滚动条样式 */
.log-output::-webkit-scrollbar {
  width: 8px;
}
.log-output::-webkit-scrollbar-thumb {
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.2);
}

.gap-2 {
  gap: 8px;
}

.gap-4 {
  gap: 16px;
}
</style>
