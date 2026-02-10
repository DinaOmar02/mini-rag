from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
import aiofiles
import os
import logging
from .schemes import ProcessRequest


logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data"],
)


@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str,file: UploadFile,
                       app_settings:Settings = Depends(get_settings)):
    
    data_controller = DataController()
    isvalid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not isvalid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": result_signal
                     }
            )
    
    project_file_path, file_id = data_controller.generate_filepath(
        original_filename=file.filename, project_id=project_id) 
    

    try:
        async with aiofiles.open(project_file_path, 'wb') as f:
            while chunk := await file.read(ResponseSignal.FILE_CHUNK_SIZE.value):
             await f.write(chunk)    
   
    except Exception as e:
        logging.error(f"Error while uploading file: {e}")
        return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": ResponseSignal.FILE_UPLOAD_FAILED.value
                }
            )
                                
    return JSONResponse(
        content={
            "message": f"File {file.filename} uploaded successfully.",
            "file_id": file_id
        }
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(project_id: str, process_request: ProcessRequest):

    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size

    process_controller = ProcessController(project_id=project_id)

    file_contetn = process_controller.get_file_content(file_id=file_id)

    content_chunks = process_controller.get_content_chunks(
        content=file_contetn,
        chunk_size=chunk_size,
        chunk_overlap=overlap_size
    )

    if content_chunks is None or len(content_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": ResponseSignal.FILE_PROCESSING_FAILED.value
            }
        )
    
    return content_chunks
