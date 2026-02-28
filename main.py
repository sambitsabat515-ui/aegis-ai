import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import logging
import os
import sys
import subprocess
import webbrowser
import uvicorn

from core.vision import VisionWatcher
from core.audio import AudioEngine
from core.ai_engine import AIEngine
from core.app_launcher import AppLauncher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# PyInstaller creates a temp folder and stores path in _MEIPASS
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

ui_dir = os.path.join(base_dir, "ui")

# Mount the UI directory
app.mount("/ui", StaticFiles(directory=ui_dir), name="ui")

# Global instances
ai_engine = AIEngine()
audio_engine = AudioEngine(ai_engine)
vision_watcher = VisionWatcher(ai_engine)
app_launcher = AppLauncher()

# Websocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")

manager = ConnectionManager()

# Background task to send UI updates
async def state_broadcaster():
    while True:
        try:
            state = ai_engine.get_state()
            await manager.broadcast(state)
        except Exception as e:
            logger.error(f"Error in state broadcaster: {e}")
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Aegis AI components...")
    # Start background watchers
    asyncio.create_task(state_broadcaster())
    vision_watcher.start()
    audio_engine.start()
    
    # Open the browser automatically in App Mode (looks like native Desktop App)
    url = "http://localhost:8000"
    try:
        subprocess.Popen(f'start msedge --app={url}', shell=True)
    except Exception:
        webbrowser.open(url)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Aegis AI components...")
    vision_watcher.stop()
    audio_engine.stop()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Not expecting client messages for now
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/dismiss")
async def dismiss_alerts():
    ai_engine.clear_alerts()
    return {"status": "success"}

@app.get("/api/apps")
async def get_apps():
    return {"apps": app_launcher.get_available_apps()}

@app.get("/")
async def get():
    index_path = os.path.join(ui_dir, "index.html")
    with open(index_path) as f:
        return HTMLResponse(f.read())

if __name__ == "__main__":
    # Fix for PyInstaller --windowed mode where sys.stdout/stderr are None
    if sys.stdout is None:
        class DummyStdout:
            def isatty(self): return False
            def write(self, *args, **kwargs): pass
            def flush(self): pass
        sys.stdout = DummyStdout()
    if sys.stderr is None:
        class DummyStderr:
            def isatty(self): return False
            def write(self, *args, **kwargs): pass
            def flush(self): pass
        sys.stderr = DummyStderr()

    uvicorn.run(app, host="127.0.0.1", port=8000)
