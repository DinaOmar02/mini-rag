from urllib import request

from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
import aiofiles
import os
import logging
from .schemes import ProcessRequest
from models.ProjectModel import ProjectModel
from models.db_schemes import DataChunk
from models.ChunkModel import ChunkModel


logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data"],
)


@data_router.post("/upload/{project_id}")
async def upload_file(request:Request, project_id: str,file: UploadFile,
                       app_settings:Settings = Depends(get_settings)):
    
    project_model = ProjectModel(
        db_client= request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)
    
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
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):

    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size

    project_model = ProjectModel(
        db_client= request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    process_controller = ProcessController(project_id=project_id)

    file_contetn = process_controller.get_file_content(file_id=file_id)

    file_chunks = process_controller.get_content_chunks(
        content=file_contetn,
        chunk_size=chunk_size,
        chunk_overlap=overlap_size
    )

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": ResponseSignal.FILE_PROCESSING_FAILED.value
            }
        )
    
    
    file_chunks_records = [
        DataChunk(
        chunk_text= chunk.page_content,
        chunk_metadata= chunk.metadata,
        chunk_project_id= i+1,
        chunk_order= project.id,
        )

        for i, chunk in enumerate(file_chunks)
    ]

    chunk_model = ChunkModel(db_client=request.app.db_client)
    
    no_records = chunk_model.insert_many_chunks(file_chunks_records)

    return no_records

