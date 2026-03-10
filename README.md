# Bilibili 下载工具

当前版本已拆成前后端分离结构：

- 后端：`bilibili_media_webui.py`
  - 提供本地 API
  - 执行缓存转 MP4、BBDown 下载、工具探测、登录态查询
  - 生产环境自动托管 `frontend/dist`
- 前端：`frontend/`
  - Vue 3 + TypeScript + Vite
  - 组件化页面、持久化设置、独立构建

## 开发

1. 启动后端 API

```powershell
python .\bilibili_media_webui.py --no-open
```

2. 启动前端开发服务器

```powershell
cd .\frontend
npm install
npm run dev
```

默认会通过 Vite 代理把 `/api` 和 `/healthz` 转发到 `http://127.0.0.1:8767`。

如果你的后端端口不是 `8767`，可复制 `frontend/.env.example` 为 `.env.local` 并修改：

```env
VITE_DEV_API_TARGET=http://127.0.0.1:8767
```

## 生产构建

```powershell
cd .\frontend
npm install
npm run build
```

构建完成后，重新启动：

```powershell
python .\bilibili_media_webui.py
```

后端会优先返回 `frontend/dist/index.html` 和静态资源；如果 `dist` 不存在，则回退到旧的内嵌页面。
