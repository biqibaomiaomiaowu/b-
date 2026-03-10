# Bilibili 下载工具 WebUI

基于前后端分离架构的现代 Bilibili 下载与缓存转换工作台。

## 架构说明

- **后端 (`backend/` & `main.py`)**
  - 基于 **FastAPI** + Python 3.12+ 编写。
  - 提供稳定、类型安全的本地 REST API。
  - 负责执行 BBDown 下载调度、本地缓存转 MP4、第三方工具路径探测、账号登录状态查询。
  - 在生产模式下自动挂载并提供静态资源分发。
- **前端 (`frontend/`)**
  - 基于 **Vue 3 + TypeScript + Vite**，界面采用 **Vuetify** 极简风格重构。
  - 提供完整的暗色/亮色模式支持、自适应布局。
  - 支持复杂参数的便捷配置与持久化。

## 如何启动与运行

### 选项一：开发模式（分离启动）

这种模式适合对界面或后端进行调试和二次开发。

**1. 启动后端 API 服务**

建议使用虚拟环境（如 `venv` 或 `conda`）。
```bash
# 安装后端依赖
pip install -r requirements.txt

# 启动后端服务
python main.py --no-open
```
*后端服务默认会启动在 `127.0.0.1:8767`。*

**2. 启动前端开发服务器**

请另外打开一个终端窗口：
```bash
# 进入前端目录
cd frontend

# 安装前端依赖
npm install

# 启动 Vite 开发服务器
npm run dev
```
*启动成功后，浏览器打开终端输出的 Vite 本地地址（通常是 `http://127.0.0.1:5173`）即可使用。前端会自动通过 Vite 代理把 `/api` 请求转发到后端的 `8767` 端口。*

> 如果你需要更改后端的代理目标地址，可以在 `frontend/` 下复制 `.env.example` 并重命名为 `.env.local`，然后修改其中的 `VITE_DEV_API_TARGET`。

---

### 选项二：生产构建与运行（整合启动）

这种模式适合日常的最终使用，只启动一个终端窗口即可体验完整的前后端整合。

**1. 打包前端静态资源**
```bash
cd frontend
npm install
npm run build
```
这会在 `frontend/dist` 目录下生成打包好的静态文件。

**2. 启动整合服务**
回到项目根目录执行：
```bash
python main.py
```
FastAPI 后端会自动检测 `frontend/dist` 目录并将其托管，浏览器稍后会自动打开以展示完整的 WebUI。

## 命令行参数

`main.py` 支持以下参数：

- `--host`: 监听地址，默认 `127.0.0.1`。
- `--port`: 监听端口，默认 `8767`。
- `--no-open`: 启动服务后不自动打开浏览器。
