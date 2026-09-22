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
from models.AssetModel import AssetModel
from models.enums import AssetTypeEnum
from models.db_schemes import Asset
from controllers import NLPController



logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data"],
)


@data_router.post("/upload/{project_id}")
async def upload_file(request:Request, project_id: int,file: UploadFile,
                       app_settings:Settings = Depends(get_settings)):
    
    project_model = await ProjectModel.create_instance(
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
    
    asset_model = await AssetModel.create_instance(
        db_client = request.app.db_client
    )

    asset_resource = Asset(
        asset_project_id=project.project_id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(project_file_path)
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)
                                
    return JSONResponse(
        content={
            "message": f"File {file.filename} uploaded successfully.",
            "file_id": str(file_id),
        }
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: int, process_request: ProcessRequest):

    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client= request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    nlp_controller = NLPController(
        vector_db_client = request.app.vector_db_client,
        embedding_client = request.app.embedding_client,
        generation_client = request.app.generation_client,
        template_parser = request.app.template_parser
        )

    process_controller = ProcessController(project_id=project_id)

    asset_model = await AssetModel.create_instance(
            db_client=request.app.db_client
        )

    project_files_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            project_id = project.project_id,
            asset_name = process_request.file_id
        )

        if asset_record is None:
            return JSONResponse(

                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": ResponseSignal.FILE_ID_ERROR.value
                }
            )
        project_files_ids = {
            asset_record.asset_id: asset_record.asset_name
        }

    else:
        
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.project_id,
            asset_type = AssetTypeEnum.FILE.value,
            )
        
        project_files_ids = {
            record.asset_id: record.asset_name
            for record in project_files
        }
    
    no_records = 0
    no_files = 0

    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    if do_reset ==1:
      collection_name = nlp_controller.create_collection_name(project_id=project.project_id)

    # Delete associated vectors
      _ = await request.app.vector_db_client.delete_collection(collection_name=collection_name)

    # Delete associated chunks
      _ = await chunk_model.delete_chunks_by_project_id(project_id = project.project_id)

    for asset_id, file_id in project_files_ids.items():

        file_contetn = process_controller.get_file_content(file_id=file_id)

        if file_contetn is None:
            logger.error(f"Error while processing file: {file_id}")
            continue

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
            chunk_project_id= project.project_id,
            chunk_order= i+1,
            chunk_asset_id = asset_id
            )

            for i, chunk in enumerate(file_chunks)
        ]
                
        no_records += await chunk_model.insert_many_chunks(file_chunks_records)
        no_files += 1

    return JSONResponse(
           content={
            "signal": ResponseSignal.FILE_PROCEESED_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files": no_files
          }
      )

