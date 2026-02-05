from fastapi import FastAPI, APIRouter, Depends, UploadFile
import os

from helpers import get_settings, Settings
from controllers import DataController

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data"],
)


@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str,file: UploadFile,
                       app_settings:Settings = Depends(get_settings)):
    
    return DataController.validate_file_type(file)
