from fastapi import WebSocket
from typing import Dict, List
import asyncio

CONNECTIONS = []


class ConnectionManager:
    # INITIALIZE THE LIST AND CONNECTION
    def __init__(self):
        self.active_connections: List[Dict[int, WebSocket]] = CONNECTIONS

    # CONNECT TO WEBSOCKET AND APPEND TO THE LIST
    async def connect(self, websocket: WebSocket, connection_id: int):
        await websocket.accept()
        self.active_connections.append({connection_id: websocket})

    # PURGE WEBSOCKET LIST STORE
    def disconnect(self, user_id: int):
        for web_dict in self.active_connections:
            if web_dict.get(user_id):
                self.active_connections.remove(web_dict)

    # SEND MESSAGE AFTER WEBSOCKET IS ALIVE
    async def send_personal_message(self, message: dict):
        user_ws = self.get_ws(message["user_id"])
        if user_ws != None:
            websocket: WebSocket = user_ws
            await websocket.send_json(message)
            return True
        return False

    # Keep the WebSocket alive.
    async def ping(self, websocket: WebSocket):
        await websocket.send_text("Nil")

    # Trigger to recieve message from the WebSocket
    async def reply(self, websocket: WebSocket):
        await websocket.send_text("Reply Pong")

    # Listening to the Websocket and sending message.
    async def pong(self, websocket: WebSocket):
        await self.reply(websocket)
        try:
            pong = await asyncio.wait_for(websocket.receive_text(), timeout=5)
            if pong == "pong":
                return True
            else:
                return False

        except asyncio.exceptions.TimeoutError as e:
            return False

    # Fetch WebSocket and return them if it exists.
    def get_ws(self, user_id: int):
        for web_dict in self.active_connections:
            if web_dict.get(user_id):
                return web_dict[user_id]

    # Send a retry message to a user WebSocket
    async def personal_notification(self, message: dict):
        connection_check = self.get_ws(message["message"]["user_id"])
        if connection_check:
            connection_check: WebSocket
            await connection_check.send_json(message)
            await asyncio.sleep(2)
            return True
        else:
            del self.active_connections[message["message"]["user_id"]]
            return False


manager = ConnectionManager()
