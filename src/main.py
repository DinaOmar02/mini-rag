from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from helpers import get_settings

#from dotenv import load_dotenv  replaced by helpers/config.py
#load_dotenv(".env")   replaced by helpers/config.py

import os
from routes import base, data

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.mongo_connect= AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client= app.mongo_connect[settings.MONGODB_DATABASE]


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_connect.close()



app.include_router(base.base_router)
app.include_router(data.data_router)