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
  <v-card class="rounded-lg top-accent-line panel-card" flat>
    <v-card-text>
      <div class="d-flex justify-space-between align-start mb-4">
        <div>
          <div class="text-overline text-medium-emphasis">队列模式</div>
          <div class="text-h6 font-weight-bold">批量任务队列</div>
          <div class="text-body-2 text-medium-emphasis mt-1">适合整理一组链接连续执行，保留统一日志，减少重复粘贴与逐条确认。</div>
        </div>
        <v-chip size="small" color="orange-darken-3" variant="tonal" class="font-weight-bold">顺序执行</v-chip>
      </div>

      <v-form @submit.prevent="emit('run')">
        <v-textarea
          v-model="form.urlsText"
          label="批量链接 / BV / av / ep / ss"
          placeholder="每行一个链接、BV 号或分享文本&#10;https://www.bilibili.com/video/BV...&#10;BV1494y1C72o&#10;https://www.bilibili.com/bangumi/play/ss..."
          variant="outlined"
          rows="8"
          auto-grow
          hint="支持一行一个链接顺序执行，也支持直接粘贴标题加链接的分享文本。"
          persistent-hint
          class="mb-3 code-textarea"
        ></v-textarea>

        <div class="mb-4">
          <v-switch
            v-model="form.continueOnError"
            label="单个失败后继续后续任务"
            color="primary"
            density="compact"
            hide-details
          ></v-switch>
        </div>

        <div class="d-flex gap-2">
          <v-btn
            color="primary"
            type="submit"
            :loading="props.busy"
            :disabled="props.busy"
            elevation="1"
          >
            开始批量下载
          </v-btn>
          <v-btn
            variant="outlined"
            @click="emit('fillExample')"
          >
            填入示例
          </v-btn>
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
  background: linear-gradient(90deg, #f57c00, rgba(245, 124, 0, 0.2));
}

.code-textarea :deep(textarea) {
  font-family: "Cascadia Code", "JetBrains Mono", Consolas, monospace;
  font-size: 14px;
  line-height: 1.6;
}

.gap-2 {
  gap: 8px;
}
</style>
