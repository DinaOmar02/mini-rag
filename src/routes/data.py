from fastapi import FastAPI, APIRouter, Depends
import os

from helpers.config import get_settings, Settings

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data"],
)


@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str, app_settings:Settings = Depends(get_settings)):
    allowed_extensions = app_settings.FILE_ALLOWED_EXTENSIONS
    max_size = app_settings.FILE_MAX_SIZE
