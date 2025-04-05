import uvicorn
from fastapi import FastAPI
from api import routers
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Telegram Account Manager")
for router in routers:
    app.include_router(router)

# Статика на уровне приложения
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
