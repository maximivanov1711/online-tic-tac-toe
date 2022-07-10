from tkinter import W
from fastapi import FastAPI, WebSocket, WebSocketDisconnect 
from typing import List


app = FastAPI()


class ConnectionManager():
    def __init__(self) -> None:
            self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()

        if len(self.active_connections) == 2:
            await websocket.close(4000)
            return
        
        self.active_connections.append(websocket)

        if len(self.active_connections) == 1:
            await websocket.send_json({
                'type': 'connection',
                'player': 'x'
            })
        elif len(self.active_connections) == 2:
            await websocket.send_json({
                'type': 'connection',
                'player': 'o'
            })

            await self.active_connections[0].send_json({
                'type': 'start'
            })
    
    async def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

        await self.active_connections[0].send_json({
            'type': 'disconnect'
        })
    
    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)

    async def broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # await manager.broadcast(f"User {client_id} says: {data}")
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

