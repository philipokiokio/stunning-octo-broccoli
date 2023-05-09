from fastapi import FastAPI
from src.notification.triger_router import trigger, manager


app = FastAPI()

app.include_router(trigger)


@app.get("/", status_code=200)
def root():
    print(manager.active_connections)
    return {
        "message": "notification proof of concept",
    }
