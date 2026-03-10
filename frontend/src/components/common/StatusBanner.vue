<script setup lang="ts">
import { computed } from 'vue'

import type { StatusKind } from '@/types/api'

const props = defineProps<{
  text: string
  kind?: StatusKind
}>()

const bannerClassName = computed(() => ['status-banner', props.kind ? `is-${props.kind}` : ''].filter(Boolean).join(' '))
</script>

<template>
  <div :class="bannerClassName">
    {{ text }}
  </div>
</template>

<style scoped>
.status-banner {
  border-radius: 16px;
  padding: 12px 14px;
  background: rgba(0, 87, 217, 0.1);
  color: var(--text);
  line-height: 1.6;
}

.is-ok {
  background: rgba(29, 138, 82, 0.12);
  color: var(--ok);
}

.is-warn {
  background: rgba(185, 121, 16, 0.12);
  color: var(--warn);
}

.is-error {
  background: rgba(193, 59, 45, 0.12);
  color: var(--error);
}
</style>
