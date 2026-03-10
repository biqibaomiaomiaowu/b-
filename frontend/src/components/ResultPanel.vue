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
  <section class="result-card">
    <div class="result-head">
      <div>
        <p class="eyebrow">执行结果</p>
        <h2 class="title">运行结果</h2>
        <p class="summary">这一栏固定保留命令、退出码和完整输出，方便复现、排错和保存现场。</p>
      </div>
      <div class="actions">
        <button class="secondary" type="button" @click="emit('copyCommand')">复制命令</button>
        <button class="secondary" type="button" @click="emit('saveSettings')">保存设置</button>
        <button class="secondary" type="button" @click="emit('clearSettings')">清除已保存设置</button>
        <button class="secondary" type="button" @click="emit('clearLog')">清空日志</button>
      </div>
    </div>

    <StatusBanner :text="statusText" :kind="statusKind" />

    <div class="terminal-bar">
      <span class="terminal-dot terminal-dot--red"></span>
      <span class="terminal-dot terminal-dot--yellow"></span>
      <span class="terminal-dot terminal-dot--green"></span>
      <span class="terminal-label">local session</span>
    </div>

    <dl class="kv-list">
      <div class="kv-item">
        <dt>命令</dt>
        <dd>{{ result.command || '-' }}</dd>
      </div>
      <div class="kv-item">
        <dt>退出码</dt>
        <dd>{{ result.returncode ?? '-' }}</dd>
      </div>
      <div class="kv-item">
        <dt>时间</dt>
        <dd>{{ result.finished_at || '-' }}</dd>
      </div>
    </dl>

    <pre class="log-output">{{ combinedLog }}</pre>

    <p class="footer">
      启动地址：<span>{{ serverUrl }}</span>
      <span class="footer-separator">·</span>
      参考：
      <a href="https://github.com/nilaoda/BBDown" target="_blank" rel="noreferrer">BBDown</a>
    </p>
  </section>
</template>

<style scoped>
.result-card {
  display: grid;
  gap: 18px;
  border-radius: var(--radius-xl);
  padding: 24px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(248, 251, 255, 0.86));
  border: 1px solid var(--panel-border);
  box-shadow: var(--shadow);
  backdrop-filter: blur(18px);
  animation: floatUp 580ms ease both;
}

.result-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.eyebrow {
  margin: 0 0 6px;
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
  max-width: 34ch;
  color: var(--muted);
  line-height: 1.7;
  font-size: 14px;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.secondary {
  min-height: 42px;
  padding: 0 16px;
  border: 1px solid var(--panel-border);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
  color: var(--text);
}

.terminal-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(16, 32, 51, 0.06);
}

.terminal-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.terminal-dot--red {
  background: #eb6c63;
}

.terminal-dot--yellow {
  background: #e4b13e;
}

.terminal-dot--green {
  background: #47b56b;
}

.terminal-label {
  margin-left: 6px;
  color: var(--muted);
  font-size: 13px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.kv-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin: 0;
}

.kv-item {
  padding: 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(34, 67, 96, 0.08);
}

.kv-item dt {
  margin-bottom: 8px;
  color: var(--muted);
  font-size: 13px;
}

.kv-item dd {
  margin: 0;
  font-weight: 600;
  word-break: break-word;
}

.log-output {
  margin: 0;
  min-height: 280px;
  padding: 18px;
  border-radius: 22px;
  background:
    linear-gradient(180deg, rgba(13, 24, 38, 0.98), rgba(17, 33, 52, 0.98)),
    radial-gradient(circle at top right, rgba(14, 91, 216, 0.18), transparent 24%);
  color: #d4e2f3;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.68;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.footer {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.footer-separator {
  margin: 0 8px;
}

@media (max-width: 900px) {
  .result-head {
    flex-direction: column;
  }

  .actions {
    justify-content: flex-start;
  }

  .kv-list {
    grid-template-columns: 1fr;
  }
}
</style>
