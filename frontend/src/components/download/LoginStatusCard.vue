<script setup lang="ts">
import StatusBanner from '@/components/common/StatusBanner.vue'
import type { LoginStatus } from '@/types/api'

const props = defineProps<{
  loginStatus: LoginStatus
}>()

const emit = defineEmits<{
  refresh: []
  loginWeb: []
  loginTv: []
  clear: []
}>()
</script>

<template>
  <v-card variant="outlined" class="rounded-lg pa-4 login-card">
    <div class="d-flex justify-space-between align-start mb-3">
      <div>
        <div class="text-subtitle-1 font-weight-bold">账号状态</div>
        <div class="text-caption text-medium-emphasis">登录信息会从 BBDown 的数据文件读取。</div>
      </div>
      <v-chip
        :color="props.loginStatus.logged_in ? 'success' : 'warning'"
        variant="tonal"
        class="px-3"
      >
        {{ props.loginStatus.logged_in ? '已登录' : '未登录' }}
      </v-chip>
    </div>

    <v-row dense class="mb-3">
      <v-col cols="6">
        <v-card variant="flat" class="bg-surface-light pa-2 rounded text-center border">
          <div class="text-caption text-medium-emphasis">账号昵称</div>
          <div class="text-body-2 font-weight-bold text-truncate" :title="props.loginStatus.account_name || '-'">{{ props.loginStatus.account_name || '-' }}</div>
        </v-card>
      </v-col>
      <v-col cols="6">
        <v-card variant="flat" class="bg-surface-light pa-2 rounded text-center border">
          <div class="text-caption text-medium-emphasis">UID</div>
          <div class="text-body-2 font-weight-bold text-truncate" :title="props.loginStatus.uid || '-'">{{ props.loginStatus.uid || '-' }}</div>
        </v-card>
      </v-col>
      <v-col cols="6">
        <v-card variant="flat" class="bg-surface-light pa-2 rounded text-center border">
          <div class="text-caption text-medium-emphasis">登录类型</div>
          <div class="text-body-2 font-weight-bold">{{ props.loginStatus.login_type || '-' }}</div>
        </v-card>
      </v-col>
      <v-col cols="6">
        <v-card variant="flat" class="bg-surface-light pa-2 rounded text-center border">
          <div class="text-caption text-medium-emphasis">过期时间</div>
          <div class="text-body-2 font-weight-bold">{{ props.loginStatus.expires_at || '-' }}</div>
        </v-card>
      </v-col>
    </v-row>

    <div v-if="props.loginStatus.message" class="mb-3">
      <StatusBanner :text="props.loginStatus.message" :kind="props.loginStatus.logged_in ? 'ok' : 'warn'" />
    </div>

    <div class="d-flex flex-wrap gap-2">
      <v-btn variant="outlined" size="small" @click="emit('refresh')">刷新状态</v-btn>
      <v-btn variant="outlined" size="small" @click="emit('loginWeb')">网页登录</v-btn>
      <v-btn variant="outlined" size="small" @click="emit('loginTv')">TV 登录</v-btn>
      <v-btn variant="outlined" size="small" color="error" @click="emit('clear')">退出登录</v-btn>
    </div>
  </v-card>
</template>

<style scoped>
.login-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  background: rgba(var(--v-theme-surface), 0.6);
}

.gap-2 {
  gap: 8px;
}
</style>
