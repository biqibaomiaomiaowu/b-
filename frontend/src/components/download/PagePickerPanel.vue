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
  <section v-if="props.items.length" class="sub-panel">
    <div class="sub-head">
      <div>
        <h3 class="sub-title">分 P / 剧集可视化选择</h3>
        <p class="sub-text">已选择 {{ selectedCount }}/{{ props.items.length }} 项。</p>
      </div>
      <button class="secondary" type="button" @click="emit('refresh')">重新解析列表</button>
    </div>

    <StatusBanner :text="hintText" kind="ok" />

    <div class="actions">
      <button class="secondary" type="button" @click="selectAll">全选</button>
      <button class="secondary" type="button" @click="clearAll">清空</button>
      <button class="secondary" type="button" @click="invertSelection">反选</button>
    </div>

    <div class="picker-grid">
      <label v-for="item in props.items" :key="item.index" class="picker-item">
        <input :checked="selectedIndexes.has(item.index)" type="checkbox" @change="handleCheckboxChange(item.index, $event)" />
        <div class="picker-text">
          <strong>{{ item.label || `${item.index}. ${item.title}` }}</strong>
          <small>{{ item.subtitle || item.title }}</small>
        </div>
      </label>
    </div>
  </section>
</template>

<style scoped>
.sub-panel {
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.78), rgba(246, 250, 255, 0.72));
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
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.secondary {
  min-height: 42px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid var(--panel-border);
  background: rgba(255, 255, 255, 0.92);
  color: var(--text);
}

.picker-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.picker-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(34, 67, 96, 0.08);
  transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
}

.picker-item:hover {
  transform: translateY(-1px);
  border-color: rgba(14, 91, 216, 0.18);
  box-shadow: 0 14px 28px rgba(29, 56, 79, 0.08);
}

.picker-item input {
  margin-top: 4px;
}

.picker-text {
  display: grid;
  gap: 6px;
}

.picker-text small {
  color: var(--muted);
}

@media (max-width: 760px) {
  .sub-head {
    flex-direction: column;
  }
}
</style>
