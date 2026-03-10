<script setup lang="ts">
import { computed } from 'vue'

import StatusBanner from '@/components/common/StatusBanner.vue'
import { buildPageSpecFromIndexes, parsePageSpecIndexes } from '@/lib/pageSpec'
import type { PageItem, PagePickerMeta } from '@/types/api'

const props = defineProps<{
  items: PageItem[]
  meta: PagePickerMeta
}>()

const model = defineModel<string>({ required: true })

const emit = defineEmits<{
  refresh: []
}>()

const selectedIndexes = computed(() => parsePageSpecIndexes(model.value, props.items.length))
const hintText = computed(() => {
  const mediaTitle = props.meta.title ? `《${props.meta.title}》` : '当前链接'
  const sourceText = props.meta.source ? `数据源：${props.meta.source}` : '已解析可选列表'
  return `${mediaTitle} 共解析到 ${props.items.length} 项。${sourceText}。勾选后会自动同步到“分P / 剧集范围”。`
})

const selectedCount = computed(() => selectedIndexes.value.size)

function updateSelection(indexes: Set<number>) {
  model.value = buildPageSpecFromIndexes(indexes, props.items.length)
}

function handleCheckboxChange(index: number, event: Event) {
  const target = event.target as HTMLInputElement | null
  const indexes = new Set(selectedIndexes.value)
  if (target?.checked) {
    indexes.add(index)
  } else {
    indexes.delete(index)
  }
  updateSelection(indexes)
}

function selectAll() {
  const indexes = new Set<number>()
  for (const item of props.items) {
    indexes.add(item.index)
  }
  updateSelection(indexes)
}

function clearAll() {
  updateSelection(new Set<number>())
}

function invertSelection() {
  const indexes = new Set<number>()
  for (const item of props.items) {
    if (!selectedIndexes.value.has(item.index)) {
      indexes.add(item.index)
    }
  }
  updateSelection(indexes)
}
</script>

<template>
  <v-card v-if="props.items.length" variant="outlined" class="rounded-lg pa-4 picker-card">
    <div class="d-flex justify-space-between align-start mb-3">
      <div>
        <div class="text-subtitle-1 font-weight-bold">分 P / 剧集选择</div>
        <div class="text-caption text-medium-emphasis">已选择 {{ selectedCount }}/{{ props.items.length }} 项。</div>
      </div>
      <v-btn variant="tonal" size="small" color="primary" @click="emit('refresh')">重新解析列表</v-btn>
    </div>

    <div class="mb-3">
      <StatusBanner :text="hintText" kind="ok" />
    </div>

    <div class="d-flex flex-wrap gap-2 mb-4">
      <v-btn variant="outlined" size="small" @click="selectAll">全选</v-btn>
      <v-btn variant="outlined" size="small" @click="clearAll">清空</v-btn>
      <v-btn variant="outlined" size="small" @click="invertSelection">反选</v-btn>
    </div>

    <v-row dense class="picker-grid">
      <v-col v-for="item in props.items" :key="item.index" cols="12" sm="6" lg="4">
        <v-card
          variant="flat"
          class="pa-2 h-100 rounded border picker-item"
          :class="{'border-primary bg-primary-subtle': selectedIndexes.has(item.index), 'bg-surface-variant': !selectedIndexes.has(item.index)}"
          @click="handleCheckboxChange(item.index, { target: { checked: !selectedIndexes.has(item.index) } } as any)"
          style="cursor: pointer;"
        >
          <div class="d-flex align-start gap-2">
            <v-checkbox-btn
              :model-value="selectedIndexes.has(item.index)"
              color="primary"
              density="compact"
              class="mt-1"
              readonly
            ></v-checkbox-btn>
            <div class="flex-grow-1 overflow-hidden">
              <div class="text-body-2 font-weight-bold text-truncate" :title="item.label || `${item.index}. ${item.title}`">
                {{ item.label || `${item.index}. ${item.title}` }}
              </div>
              <div class="text-caption text-medium-emphasis text-truncate" :title="item.subtitle || item.title">
                {{ item.subtitle || item.title }}
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-card>
</template>

<style scoped>
.picker-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  background: rgba(var(--v-theme-surface), 0.6);
}

.picker-item {
  transition: all 0.2s ease;
}

.picker-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(var(--v-theme-on-surface), 0.08);
}

.bg-primary-subtle {
  background-color: rgba(var(--v-theme-primary), 0.05) !important;
}

.border-primary {
  border-color: rgba(var(--v-theme-primary), 0.5) !important;
}

.gap-2 {
  gap: 8px;
}

.picker-grid {
  max-height: 400px;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 改善滚动条样式 */
.picker-grid::-webkit-scrollbar {
  width: 6px;
}
.picker-grid::-webkit-scrollbar-thumb {
  border-radius: 3px;
  background: rgba(var(--v-theme-on-surface), 0.2);
}
</style>
