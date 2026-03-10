<script setup lang="ts">
import type { BatchForm } from '@/types/forms'

const props = defineProps<{
  busy: boolean
}>()

const form = defineModel<BatchForm>({ required: true })

const emit = defineEmits<{
  run: []
  fillExample: []
}>()
</script>

<template>
  <section class="panel-card">
    <div class="panel-head">
      <div>
        <p class="eyebrow">队列模式</p>
        <h2 class="title">批量任务队列</h2>
        <p class="summary">适合整理一组链接连续执行，保留统一日志，减少重复粘贴与逐条确认。</p>
      </div>
      <span class="tag">顺序执行</span>
    </div>

    <div class="field">
      <label class="field-label" for="batch-urls">批量链接 / BV / av / ep / ss</label>
      <textarea
        id="batch-urls"
        v-model="form.urlsText"
        class="field-textarea"
        rows="8"
        placeholder="每行一个链接、BV 号或分享文本&#10;https://www.bilibili.com/video/BV...&#10;BV1494y1C72o&#10;https://www.bilibili.com/bangumi/play/ss..."
      />
      <p class="field-help">支持一行一个链接顺序执行，也支持直接粘贴标题加链接的分享文本。</p>
    </div>

    <label class="toggle-item">
      <input v-model="form.continueOnError" type="checkbox" />
      <span>单个失败后继续后续任务</span>
    </label>

    <div class="actions">
      <button class="secondary" type="button" @click="emit('fillExample')">填入示例</button>
      <button class="primary" type="button" :disabled="props.busy" @click="emit('run')">
        {{ props.busy ? '处理中...' : '开始批量下载' }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.panel-card {
  display: grid;
  gap: 18px;
  padding: 24px;
  border-radius: var(--radius-xl);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(248, 251, 255, 0.82));
  border: 1px solid var(--panel-border);
  box-shadow: var(--shadow);
  backdrop-filter: blur(18px);
  position: relative;
  overflow: hidden;
  animation: floatUp 540ms ease both;
}

.panel-card::before {
  content: "";
  position: absolute;
  inset: 0 auto auto 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, var(--accent-warm), rgba(220, 122, 48, 0.12));
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
  max-width: 38ch;
  color: var(--muted);
  line-height: 1.7;
  font-size: 14px;
}

.tag {
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(220, 122, 48, 0.1);
  color: #9b4a16;
  font-size: 13px;
  font-weight: 700;
}

.field {
  display: grid;
  gap: 8px;
}

.field-label {
  font-weight: 700;
}

.field-textarea {
  width: 100%;
  resize: vertical;
  min-height: 180px;
  border: 1px solid rgba(34, 67, 96, 0.12);
  border-radius: 18px;
  padding: 14px;
  background:
    linear-gradient(180deg, rgba(17, 30, 47, 0.98), rgba(21, 37, 58, 0.96)),
    repeating-linear-gradient(180deg, rgba(255, 255, 255, 0.02) 0 1px, transparent 1px 30px);
  color: #dce8f5;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.field-help {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--muted);
}

.toggle-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 42px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.8);
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

.primary:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

@media (max-width: 760px) {
  .panel-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
