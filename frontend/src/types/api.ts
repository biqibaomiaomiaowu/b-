export type StatusKind = '' | 'ok' | 'warn' | 'error'

export interface BootstrapResponse {
  default_cache_path: string
  default_bbdown: string
  quality_options: string[]
  server_url: string
  frontend_dist_ready: boolean
}

export interface LoginStatus {
  logged_in: boolean
  login_type: string
  account_name: string
  uid: string
  expires_at: string
  data_file?: string
  message: string
  raw_cookie_found?: boolean
}

export interface ToolStatus {
  key: string
  label: string
  found: boolean
  path: string
  source: string
  version: string
  searched?: string[]
}

export interface ToolDetectResponse {
  ok: boolean
  message: string
  tools: Record<string, ToolStatus>
  fields: Record<string, string>
  found_count: number
  total_count: number
}

export interface PageItem {
  index: number
  title: string
  subtitle: string
  label: string
}

export interface PagePickerMeta {
  title: string
  source: string
}

export interface OperationResult {
  command: string
  returncode: number | string
  finished_at: string
  stdout: string
  stderr: string
  error?: string
  message?: string
  normalized_url?: string
  qualities?: string[]
  pages?: PageItem[]
  pages_source?: string
  media_title?: string
  items?: OperationResult[]
  processed?: number
  succeeded?: number
  failed?: number
  skipped?: number
  continue_on_error?: boolean
}

export interface ApiResponse<T> {
  ok: boolean
  status: number
  data: T
}
