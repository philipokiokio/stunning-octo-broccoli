import base64
from fastapi import WebSocket
from typing import Dict, List
import asyncio
from src.notification.models import Repo
from src.app.database import session_scope


CONNECTIONS = []


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[Dict[int, WebSocket]] = CONNECTIONS

    def ws_serializer(self, ws: WebSocket) -> dict:
        ws = ws.__dict__
        return ws

    def ws_objectifer(self, ws: dict) -> WebSocket:
        ws_ = WebSocket(ws["scope"], ws["_receive"], ws["_send"])
        ws_.__dict__.update(ws)
        return ws_

    async def connect(self, websocket: WebSocket, connection_id: int):
        await websocket.accept()
        self.active_connections.append({connection_id: websocket})
        ws__ = self.ws_serializer(websocket)
        ws = self.ws_objectifer(ws__)
        await ws.send_json({"testing": "coding magic"})

        print(self.active_connections)

    def disconnect(self, user_id: int):
        for web_dict in self.active_connections:
            if web_dict.get(user_id):
                self.active_connections.remove(web_dict)
                print(self.active_connections)

    async def send_personal_message(self, message: dict):
        print(message)
        user_ws = self.get_ws(message["user_id"])
        print(user_ws)
        if user_ws != None:
            websocket: WebSocket = user_ws
            await websocket.send_json(message)
            return True
        return False

    async def ping(self, websocket: WebSocket):
        status = await websocket.send_text("Ping")
        print(status)

    async def pong(self, websocket: WebSocket):
        await self.ping(websocket)
        pong = await websocket.receive_text()
        print(pong)
        if pong == "pong":
            return True
        else:
            self.disconnect(websocket)
            return False

    def get_ws(self, user_id: int):
        print("this is the active connections", self.active_connections)
        for web_dict in self.active_connections:
            if web_dict.get(user_id):
                return web_dict[user_id]

    async def personal_notification(self, message: dict):
        print(message)

        connection_check = self.get_ws(message["message"]["user_id"])
        print(connection_check, "ws")
        if connection_check:
            # pong_status = await asyncio.wait_for(
            #     self.pong(connection_check), timeout=10
            # )
            # if pong_status == False:
            #     return False
            # else:
            connection_check: WebSocket
            message_status = await connection_check.send_json(message)
            print(message_status)
            await asyncio.sleep(2)
            return True
        else:
            del self.active_connections[message["message"]["user_id"]]
            return False


manager = ConnectionManager()
