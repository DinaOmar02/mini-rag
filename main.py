from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv(".env")

import os
from routes import base

app = FastAPI()
app.include_router(base.base_router)