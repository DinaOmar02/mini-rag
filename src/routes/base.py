from fastapi import FastAPI, APIRouter, Depends
import os
from controllers import BaseController
from helpers import get_settings, Settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["Base"],
)



@base_router.get("/")
async def welcome(app_settings:Settings = Depends(get_settings)):
    #app_name = os.getenv("APP_NAME")   replaced by helpers/config.py
    #app_version = os.getenv("APP_VERSION") relaced by helpers/config.py
    
    app_name = BaseController().app_settings.APP_NAME
    app_version = BaseController().app_settings.APP_VERSION

    return  {
        "App Name": app_name,
        "App Version": app_version
        }

