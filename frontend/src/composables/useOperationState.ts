import { reactive, shallowRef } from 'vue'

import { createEmptyResult } from '@/lib/defaults'
import type { OperationResult, StatusKind } from '@/types/api'

export function useOperationState() {
  const busy = shallowRef(false)
  const statusText = shallowRef('等待开始。')
  const statusKind = shallowRef<StatusKind>('')
  const result = reactive<OperationResult>(createEmptyResult())

  function setStatus(text: string, kind: StatusKind = '') {
    statusText.value = text
    statusKind.value = kind
  }

  function applyResult(data: Partial<OperationResult>, ok: boolean, fallbackMessage: string) {
    const nextResult = {
      ...createEmptyResult(),
      ...data,
    }

    Object.assign(result, nextResult)

    const successMessage = String(nextResult.message || fallbackMessage || '操作已完成。')
    const failureMessage = String(nextResult.error || nextResult.message || '操作失败，请查看日志。')
    setStatus(ok ? successMessage : failureMessage, ok ? 'ok' : 'error')
  }

  function setPending() {
    result.command = '-'
    result.returncode = '-'
    result.finished_at = '-'
    result.stdout = '运行中...'
    result.stderr = ''
  }

  function clearResult() {
    Object.assign(result, createEmptyResult())
    setStatus('日志已清空。')
  }

  return {
    busy,
    statusText,
    statusKind,
    result,
    setStatus,
    applyResult,
    setPending,
    clearResult,
  }
}
