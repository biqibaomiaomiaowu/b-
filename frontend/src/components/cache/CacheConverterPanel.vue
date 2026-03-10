<script setup lang="ts">
import type { CacheForm } from '@/types/forms'

const props = defineProps<{
  busy: boolean
}>()

const form = defineModel<CacheForm>({ required: true })

const emit = defineEmits<{
  run: []
  fillExample: []
}>()
</script>

<template>
  <section class="panel-card">
    <div class="panel-head">
      <div>
        <p class="eyebrow">模式一</p>
        <h2 class="title">缓存目录转 MP4</h2>
        <p class="summary">适合把手机或客户端缓存目录快速整理成可直接播放、归档的 MP4 文件。</p>
      </div>
      <span class="tag">本地转换</span>
    </div>

    <form class="panel-form" @submit.prevent="emit('run')">
      <div class="field">
        <label class="field-label" for="cache-input-path">缓存目录</label>
        <input id="cache-input-path" v-model="form.inputPath" class="field-input" type="text" required />
        <p class="field-help">可填单个视频缓存目录，也可填整个 <code>bilibili</code> 根目录批量处理。</p>
      </div>

      <div class="field-grid">
        <div class="field">
          <label class="field-label" for="cache-output">输出目录 / 输出文件</label>
          <input id="cache-output" v-model="form.output" class="field-input" type="text" placeholder="留空则按脚本默认规则输出" />
        </div>

        <div class="field">
          <label class="field-label" for="cache-ffmpeg">ffmpeg 路径</label>
          <input id="cache-ffmpeg" v-model="form.ffmpeg" class="field-input" type="text" />
        </div>
      </div>

      <div class="field">
        <label class="field-label" for="cache-ffprobe">ffprobe 路径</label>
        <input id="cache-ffprobe" v-model="form.ffprobe" class="field-input" type="text" placeholder="留空则自动推断" />
      </div>

      <div class="toggle-grid">
        <label class="toggle-item">
          <input v-model="form.force" type="checkbox" />
          <span>强制覆盖已有输出</span>
        </label>
        <label class="toggle-item">
          <input v-model="form.dryRun" type="checkbox" />
          <span>仅预演，不真正执行</span>
        </label>
      </div>

      <div class="actions">
        <button class="primary" type="submit" :disabled="props.busy">
          {{ props.busy ? '处理中...' : '开始转换' }}
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
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(248, 251, 255, 0.8));
  border: 1px solid var(--panel-border);
  box-shadow: var(--shadow);
  backdrop-filter: blur(18px);
  position: relative;
  overflow: hidden;
  animation: floatUp 460ms ease both;
}

.panel-card::before {
  content: "";
  position: absolute;
  inset: 0 auto auto 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, var(--accent), rgba(14, 91, 216, 0.12));
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
  max-width: 36ch;
  color: var(--muted);
  line-height: 1.7;
  font-size: 14px;
}

.tag {
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(14, 91, 216, 0.1);
  color: var(--accent-strong);
  font-size: 13px;
  font-weight: 700;
  box-shadow: inset 0 0 0 1px rgba(14, 91, 216, 0.08);
}

.panel-form,
.field-grid {
  display: grid;
  gap: 16px;
}

.field-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
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
  background: rgba(255, 255, 255, 0.86);
  color: var(--text);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.field-help {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--muted);
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
  background: rgba(255, 255, 255, 0.78);
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
  background: rgba(255, 255, 255, 0.9);
  color: var(--text);
}

.primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 760px) {
  .field-grid {
    grid-template-columns: 1fr;
  }

  .panel-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
