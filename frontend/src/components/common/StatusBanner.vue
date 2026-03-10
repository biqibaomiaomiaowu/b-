<script setup lang="ts">
import { computed } from 'vue'

import type { StatusKind } from '@/types/api'

const props = defineProps<{
  text: string
  kind?: StatusKind
}>()

const alertType = computed(() => {
  if (props.kind === 'ok') return 'success'
  if (props.kind === 'warn') return 'warning'
  if (props.kind === 'error') return 'error'
  return 'info'
})
</script>

<template>
  <v-alert
    :type="alertType"
    :text="text"
    variant="tonal"
    density="compact"
    class="text-body-2"
  ></v-alert>
</template>

<style scoped>
</style>
