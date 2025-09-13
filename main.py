from fastapi import FastAPI,WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()


@app.get('/')
def home():
    # Define the path to your HTML file
    file_path = Path('templates/home.html')

    # Read the file and return its content as an HTMLResponse
    with file_path.open('r') as file:
        return HTMLResponse(file.read())

class ConnectionManager:
    def __init__(self):
        self.active_connections:list[WebSocket] = []

    async def check_connection(self, websocket:WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self,  websocket:WebSocket,message:str):
        await websocket.send_text(message)

    async def broadcast_message(self,message:str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

''''
step1
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id:int):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Client {client_id} says: {data}")
'''

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id:int):
    await manager.check_connection(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(websocket, f"You wrote: {data}")
            await manager.broadcast_message(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast_message(f"Client #{client_id} has left the chat")


