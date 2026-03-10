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
  <section class="sub-panel">
    <div class="sub-head">
      <div>
        <h3 class="sub-title">工具路径自动发现</h3>
        <p class="sub-text">扫描系统 PATH、常见安装位置和你当前填写的路径，并回填到表单中。</p>
      </div>
      <button class="secondary" type="button" @click="emit('detect')">自动检测工具路径</button>
    </div>

    <StatusBanner :text="bannerText" :kind="bannerKind" />

    <div class="tool-grid">
      <article v-for="tool in tools" :key="tool.key" class="tool-item">
        <div class="tool-row">
          <strong>{{ tool.label || tool.key }}</strong>
          <span :class="['tool-state', tool.found ? 'is-ok' : 'is-warn']">
            {{ tool.found ? `已找到 · ${tool.source || 'detected'}` : '未找到' }}
          </span>
        </div>
        <small v-if="tool.version" class="tool-version">{{ tool.version }}</small>
        <code class="tool-path">{{ tool.path || tool.searched?.[0] || '未找到常见路径' }}</code>
      </article>
    </div>
  </section>
</template>

<style scoped>
.sub-panel {
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.78), rgba(245, 250, 255, 0.72));
  border: 1px solid rgba(34, 67, 96, 0.1);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.82);
}

.sub-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
}

.sub-title {
  margin: 0 0 6px;
  font-size: 18px;
}

.sub-text {
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
}

.secondary {
  min-height: 42px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid var(--panel-border);
  background: rgba(255, 255, 255, 0.92);
  color: var(--text);
}

.tool-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.tool-item {
  display: grid;
  gap: 8px;
  padding: 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(34, 67, 96, 0.08);
}

.tool-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.tool-state {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.is-ok {
  background: rgba(29, 138, 82, 0.12);
  color: var(--ok);
}

.is-warn {
  background: rgba(185, 121, 16, 0.12);
  color: var(--warn);
}

.tool-version {
  color: var(--muted);
}

.tool-path {
  display: block;
  padding: 10px 12px;
  border-radius: 14px;
  background: linear-gradient(160deg, #102033, #163150);
  color: #d4e2f3;
  word-break: break-all;
}

@media (max-width: 760px) {
  .sub-head {
    flex-direction: column;
  }
}
</style>
