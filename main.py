from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import asyncio
import json
import uuid
from terminal_core import TerminalSession
from boot_manager import BootManager
import os

app = FastAPI()

os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

sessions: dict = {}

@app.get("/", response_class=HTMLResponse)
async def get_terminal(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    if session_id not in sessions:
        sessions[session_id] = TerminalSession(session_id)
    
    terminal = sessions[session_id]
    
    try:
        boot_manager = BootManager(terminal)
        boot_sequence = boot_manager.generate_boot_sequence()
        
        for line in boot_sequence:
            await websocket.send_json({
                "type": "output",
                "data": line["text"],
                "color": line.get("color", "white")
            })
            await asyncio.sleep(line.get("delay", 0.05))
        
        await websocket.send_json({
            "type": "ready",
            "prompt": terminal.get_prompt()
        })
        
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "command":
                command = data["data"]
                terminal.add_to_history(command)
                
                result = await terminal.execute(command)
                
                if result["type"] == "shutdown":
                    for line in result["sequence"]:
                        await websocket.send_json({
                            "type": "output",
                            "data": line["text"],
                            "color": line.get("color", "white")
                        })
                        await asyncio.sleep(line.get("delay", 0.1))
                    
                    if result.get("reboot"):
                        await asyncio.sleep(1)
                        boot_sequence = boot_manager.generate_boot_sequence()
                        for line in boot_sequence:
                            await websocket.send_json({
                                "type": "output",
                                "data": line["text"],
                                "color": line.get("color", "white")
                            })
                            await asyncio.sleep(line.get("delay", 0.05))
                        await websocket.send_json({
                            "type": "ready",
                            "prompt": terminal.get_prompt()
                        })
                    else:
                        await websocket.send_json({"type": "poweroff"})
                        break
                else:
                    for line in result.get("output", []):
                        await websocket.send_json({
                            "type": "output",
                            "data": line
                        })
                    
                    await websocket.send_json({
                        "type": "prompt",
                        "data": terminal.get_prompt()
                    })
            
            elif data["type"] == "sync_fs":
                terminal.filesystem.sync_from_indexeddb(data["data"])
            
            elif data["type"] == "get_fs":
                fs_data = terminal.filesystem.export_to_indexeddb()
                await websocket.send_json({
                    "type": "fs_data",
                    "data": fs_data
                })
            
            elif data["type"] == "signal":
                terminal.handle_signal(data["signal"])
            
            elif data["type"] == "resize":
                terminal.resize(data["cols"], data["rows"])
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "data": str(e)
        })

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
