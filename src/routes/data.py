from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController, ProjectController
from models import ResponseSignal
import aiofiles
import os


data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data"],
)


@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str,file: UploadFile,
                       app_settings:Settings = Depends(get_settings)):
    
    
    isvalid, result_signal = DataController().validate_uploaded_file(file=file)

    if not isvalid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": result_signal
                     }
            )
    
    project_file_path = os.path.join(ProjectController().get_project_path(project_id=project_id), file.filename)   

    async with aiofiles.open(project_file_path, 'wb') as f:
        while chunk := await file.read(ResponseSignal.FILE_CHUNK_SIZE.value):
            await f.write(chunk)    
   
                                
    return JSONResponse(
        content={
            "message": f"File {file.filename} uploaded successfully."
        }
    )