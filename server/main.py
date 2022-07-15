from tkinter import W
from fastapi import FastAPI, WebSocket, WebSocketDisconnect 
from typing import List


def debug(obj):
    global DEBUG
    if DEBUG:
        print(obj)


DEBUG = True


app = FastAPI()


class ConnectionManager():
    def __init__(self):
            self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()

        if len(self.active_connections) == 2:
            await websocket.close(4000)

            return False
        
        self.active_connections.append(websocket)

        if len(self.active_connections) == 1:
            await websocket.send_json({
                'type': 'connection',
                'player': 'x'
            })

            self.connected_player = 'x'
            return True
        elif len(self.active_connections) == 2:
            await websocket.send_json({
                'type': 'connection',
                'player': 'o'
            })

            await self.active_connections[0].send_json({
                'type': 'start'
            })

            self.connected_player = 'o'
            return True
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

        if self.active_connections:
            await self.active_connections[0].send_json({
                'type': 'disconnect'
            })

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


class GameManager():
    def __init__(self):
        self.board = [
            ['*', '*', '*'], 
            ['*', '*', '*'],
            ['*', '*', '*']
        ]

        self.players = {}

        self.is_game_started = False
    
    def add_player(self, player: str, websocket: WebSocket):
        self.players[player] = websocket
    
    def start(self):
        self.is_game_started = True
        self.current_player = 'x'
    
    async def process_turn(self, turn: dict):
        debug(turn)

        if not self.is_game_started:
            return

        player = turn['player']
        cell = turn['cell']

        if self.current_player != player:
            await manager.broadcast({
                'type': 'denied',
                'player': player,
                'message': 'Wait for your turn'
            })

            return
        
        await manager.broadcast({
                'type': 'turn',
                'player': player,
                'cell': cell
            })


            


manager = ConnectionManager()
game = GameManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    is_player_connected = await manager.connect(websocket)
    
    if not is_player_connected:
        return
    
    connected_player = manager.connected_player

    game.add_player(connected_player, websocket)
    
    if connected_player == 'o':
        game.start()

    try:
        while True:
            turn = await websocket.receive_json()
            
            await game.process_turn(turn)
            
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

