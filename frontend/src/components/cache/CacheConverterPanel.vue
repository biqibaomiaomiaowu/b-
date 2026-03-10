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
  <v-card class="h-100 rounded-lg top-accent-line panel-card" flat>
    <v-card-text>
      <div class="d-flex justify-space-between align-start mb-4">
        <div>
          <div class="text-overline text-medium-emphasis">模式一</div>
          <div class="text-h6 font-weight-bold">缓存目录转 MP4</div>
          <div class="text-body-2 text-medium-emphasis mt-1">适合把手机或客户端缓存目录快速整理成可直接播放、归档的 MP4 文件。</div>
        </div>
        <v-chip color="primary" variant="tonal" class="font-weight-bold px-3">本地转换</v-chip>
      </div>

      <v-form @submit.prevent="emit('run')">
        <v-text-field
          v-model="form.inputPath"
          label="缓存目录"
          required
          variant="outlined"
          density="compact"
          hint="可填单个视频缓存目录，也可填整个 bilibili 根目录批量处理。"
          persistent-hint
          class="mb-3"
        ></v-text-field>

        <v-row dense class="mb-1">
          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.output"
              label="输出目录 / 输出文件"
              placeholder="留空则按脚本默认规则输出"
              variant="outlined"
              density="compact"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.ffmpeg"
              label="ffmpeg 路径"
              variant="outlined"
              density="compact"
            ></v-text-field>
          </v-col>
        </v-row>

        <v-text-field
          v-model="form.ffprobe"
          label="ffprobe 路径"
          placeholder="留空则自动推断"
          variant="outlined"
          density="compact"
          class="mb-1"
        ></v-text-field>

        <div class="d-flex flex-wrap gap-4 mb-4">
          <v-switch
            v-model="form.force"
            label="强制覆盖"
            color="primary"
            density="compact"
            hide-details
          ></v-switch>
          <v-switch
            v-model="form.dryRun"
            label="仅预演"
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
            开始转换
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
  background: linear-gradient(90deg, rgb(var(--v-theme-primary)), rgba(var(--v-theme-primary), 0.2));
}

.gap-2 {
  gap: 8px;
}

.gap-4 {
  gap: 16px;
}
</style>
