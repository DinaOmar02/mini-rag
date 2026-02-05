from fastapi import FastAPI

#from dotenv import load_dotenv  replaced by helpers/config.py
#load_dotenv(".env")   replaced by helpers/config.py

import os
from routes import base

app = FastAPI()
app.include_router(base.base_router)