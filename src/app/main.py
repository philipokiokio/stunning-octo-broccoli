from fastapi import FastAPI
from src.notification.triger_router import trigger


app = FastAPI()

app.include_router(trigger)


@app.get("/", status_code=200)
def root():
    return {"message": "notification proof of concept"}
