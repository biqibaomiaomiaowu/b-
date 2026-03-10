<script setup lang="ts">
import { ref } from 'vue'
import { useTheme } from 'vuetify'
import BilibiliWorkspace from '@/features/media-tool/BilibiliWorkspace.vue'

const theme = useTheme()
const isDark = ref(theme.global.current.value.dark)

function toggleTheme() {
  const newTheme = isDark.value ? 'light' : 'dark'
  theme.global.name.value = newTheme
  isDark.value = newTheme === 'dark'
}
</script>

<template>
  <v-app>
    <v-app-bar flat border density="compact">
      <v-app-bar-title>Media WebUI</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="toggleTheme">
        <v-icon>{{ isDark ? 'mdi-weather-night' : 'mdi-weather-sunny' }}</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid class="fill-height align-start">
        <BilibiliWorkspace />
      </v-container>
    </v-main>
  </v-app>
</template>
