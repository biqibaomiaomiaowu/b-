<script setup lang="ts">
import { computed } from 'vue'

import StatusBanner from '@/components/common/StatusBanner.vue'
import type { ToolDetectResponse } from '@/types/api'

const props = defineProps<{
  detection: ToolDetectResponse | null
}>()

const emit = defineEmits<{
  detect: []
}>()

const tools = computed(() => (props.detection ? Object.values(props.detection.tools) : []))
const bannerText = computed(() => props.detection?.message || '启动后会自动补全空白工具路径；你也可以手动重新检测并覆盖。')
const bannerKind = computed(() => {
  if (!props.detection) {
    return 'warn'
  }
  return props.detection.ok ? 'ok' : 'warn'
})
</script>

<template>
  <v-card variant="outlined" class="rounded-lg pa-4 tool-card">
    <div class="d-flex justify-space-between align-start mb-3">
      <div>
        <div class="text-subtitle-1 font-weight-bold">工具路径自动发现</div>
        <div class="text-caption text-medium-emphasis">扫描系统 PATH、常见安装位置和你当前填写的路径。</div>
      </div>
      <v-btn variant="tonal" size="small" color="primary" @click="emit('detect')">自动检测</v-btn>
    </div>

    <div class="mb-3">
      <StatusBanner :text="bannerText" :kind="bannerKind" />
    </div>

    <v-row dense>
      <v-col v-for="tool in tools" :key="tool.key" cols="12" sm="6" lg="4">
        <v-card variant="flat" class="bg-surface-variant pa-3 h-100 rounded d-flex flex-column">
          <div class="d-flex justify-space-between align-start mb-1">
            <span class="font-weight-bold text-body-2">{{ tool.label || tool.key }}</span>
            <v-chip
              size="x-small"
              :color="tool.found ? 'success' : 'warning'"
              variant="flat"
            >
              {{ tool.found ? `已找到 · ${tool.source || 'detected'}` : '未找到' }}
            </v-chip>
          </div>

          <div v-if="tool.version" class="text-caption text-medium-emphasis mb-1">
            {{ tool.version }}
          </div>

          <div class="mt-auto">
            <v-card variant="flat" class="bg-black text-white pa-2 rounded mt-2">
              <code class="text-caption d-block" style="word-break: break-all; white-space: pre-wrap;">{{ tool.path || tool.searched?.[0] || '未找到常见路径' }}</code>
            </v-card>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-card>
</template>

<style scoped>
.tool-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  background: rgba(var(--v-theme-surface), 0.6);
}
</style>
