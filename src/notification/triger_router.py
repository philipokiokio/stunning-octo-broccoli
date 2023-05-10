from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from src.notification.websocket_manager import manager
from src.notification.messaging_bq import mq
from pydantic import BaseModel
import time
import asyncio

trigger = APIRouter(prefix="/api/trigger", tags=["trigger_in"])


class Demonstrate(BaseModel):
    body: dict
    user_id: int


State = []


def get_current_user():
    return {"id": 1}


@trigger.post("/push-in/", status_code=200)
async def registration(demo: Demonstrate, user: dict = Depends(get_current_user)):
    demo = demo.dict()

    print(manager.active_connections)

    if manager.get_ws(demo["user_id"]):
        ws_alive = await manager.pong(manager.get_ws(demo["user_id"]))
        if ws_alive:
            await manager.send_personal_message(demo)
        else:
            mq.publish_notification(demo)
    else:
        mq.publish_notification(demo)

    State.append(demo)

    # print(State)
    return {"message": "This has been published"}


{"message": {"body": {"testing": "God abeg"}, "user_id": 1}, "delivery_tag": 2}


@trigger.websocket("/notifier/ws/")
async def notification_socket(
    websocket: WebSocket, user: dict = Depends(get_current_user)
):
    await manager.connect(websocket, user["id"])

    try:
        if manager.get_ws(user["id"]):
            user_meesage = mq.get_user_messages(user["id"])

            if user_meesage != None:
                for message in user_meesage:
                    if message != None:
                        # print(message)
                        # print(message["message"]["user_id"])
                        message_status = await manager.personal_notification(message)
                        print(message_status)
                        # delete the message from the queue if successfully sent via WebSocket
                        if message_status:
                            mq.channel.basic_ack(delivery_tag=message["delivery_tag"])

        hang = True
        while hang:
            await asyncio.sleep(3)
            await manager.ping(websocket)
            # asyncio.wait_for(websocket.ping(), timeout=5)
            # await websocket.send_text(f"Message text was: {data}")

        # await manager.pong(websocket)

    except (WebSocketDisconnect, ConnectionClosedError, ConnectionClosedOK):
        manager.disconnect(user["id"])
