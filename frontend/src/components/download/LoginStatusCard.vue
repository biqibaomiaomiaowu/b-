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
  <section class="sub-panel">
    <div class="sub-head">
      <div>
        <h3 class="sub-title">账号状态</h3>
        <p class="sub-text">登录信息会从 BBDown 的数据文件读取，并在需要时自动联动下载参数。</p>
      </div>
      <span :class="['badge', props.loginStatus.logged_in ? 'is-ok' : 'is-warn']">
        {{ props.loginStatus.logged_in ? '已登录' : '未登录' }}
      </span>
    </div>

    <dl class="kv-list">
      <div class="kv-item">
        <dt>账号昵称</dt>
        <dd>{{ props.loginStatus.account_name || '-' }}</dd>
      </div>
      <div class="kv-item">
        <dt>UID</dt>
        <dd>{{ props.loginStatus.uid || '-' }}</dd>
      </div>
      <div class="kv-item">
        <dt>登录类型</dt>
        <dd>{{ props.loginStatus.login_type || '-' }}</dd>
      </div>
      <div class="kv-item">
        <dt>过期时间</dt>
        <dd>{{ props.loginStatus.expires_at || '-' }}</dd>
      </div>
    </dl>

    <StatusBanner :text="props.loginStatus.message" :kind="props.loginStatus.logged_in ? 'ok' : 'warn'" />

    <div class="actions">
      <button class="secondary" type="button" @click="emit('refresh')">刷新登录状态</button>
      <button class="secondary" type="button" @click="emit('loginWeb')">网页登录</button>
      <button class="secondary" type="button" @click="emit('loginTv')">TV 登录</button>
      <button class="secondary" type="button" @click="emit('clear')">退出登录</button>
    </div>
  </section>
</template>

<style scoped>
.sub-panel {
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.78), rgba(245, 250, 255, 0.72));
  border: 1px solid rgba(34, 67, 96, 0.1);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.82);
}

.sub-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.sub-title {
  margin: 0 0 6px;
  font-size: 18px;
}

.sub-text {
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
}

.badge {
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.is-ok {
  background: rgba(29, 138, 82, 0.12);
  color: var(--ok);
}

.is-warn {
  background: rgba(185, 121, 16, 0.12);
  color: var(--warn);
}

.kv-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 0;
}

.kv-item {
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(34, 67, 96, 0.06);
}

.kv-item dt {
  margin-bottom: 6px;
  color: var(--muted);
  font-size: 13px;
}

.kv-item dd {
  margin: 0;
  font-weight: 600;
  word-break: break-word;
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

@media (max-width: 760px) {
  .sub-head {
    flex-direction: column;
  }

  .kv-list {
    grid-template-columns: 1fr;
  }
}
</style>
