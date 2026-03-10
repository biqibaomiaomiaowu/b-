import argparse
import sys
import threading
import webbrowser
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from backend.api import router
from backend.constants import FRONTEND_DIST_DIR

host = "127.0.0.1"
port = 8767
no_open = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if not no_open:
        url = f"http://{host}:{port}/"
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    yield
    # Shutdown
    pass

app = FastAPI(lifespan=lifespan)
app.include_router(router)

# Optional: Serve static frontend
if FRONTEND_DIST_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST_DIR / "assets"), name="assets")

    @app.get("/")
    @app.get("/{catchall:path}")
    def serve_frontend():
        return FileResponse(FRONTEND_DIST_DIR / "index.html")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="启动 Bilibili 下载 / 转换的本地网页界面。")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址，默认 127.0.0.1")
    parser.add_argument("--port", type=int, default=8767, help="监听端口，默认 8767")
    parser.add_argument("--no-open", action="store_true", help="启动后不自动打开浏览器")
    return parser.parse_args()

def main():
    global host, port, no_open
    args = parse_args()
    host = args.host
    port = args.port
    no_open = args.no_open

    print(f"Starting API server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, log_level="info", reload=False)

if __name__ == "__main__":
    sys.exit(main())
