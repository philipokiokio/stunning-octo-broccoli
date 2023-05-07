from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from websockets.exceptions import ConnectionClosedError
from src.notification.websocket_manager import manager
from src.notification.messaging_bq import mq
from pydantic import BaseModel

trigger = APIRouter(prefix="/api/trigger", tags=["trigger_in"])


class Demonstrate(BaseModel):
    body: dict


State = []


def get_current_user():
    return {"id": 1}


@trigger.post("/push-in/", status_code=200)
def registration(demo: Demonstrate, user: dict = Depends(get_current_user)):
    demo = demo.dict()
    demo["user_id"] = user["id"]
    mq.publish_notification(demo)

    State.append(demo)

    print(State)
    return {"message": "This has been published"}


{"message": {"body": {"testing": "God abeg"}, "user_id": 1}, "delivery_tag": 2}


@trigger.websocket("/notifier/ws/")
async def notification_socket(
    websocket: WebSocket, user: dict = Depends(get_current_user)
):
    await manager.connect(websocket, user["id"])

    try:
        while True:
            data = await websocket.receive_json()

            # asyncio.wait_for(websocket.ping(), timeout=5)
            await websocket.send_text(f"Message text was: {data}")

            await mq.retry_unsent_messages(user["id"])
            # await manager.pong(websocket)

    except (WebSocketDisconnect, ConnectionClosedError):
        manager.disconnect(user["id"])
