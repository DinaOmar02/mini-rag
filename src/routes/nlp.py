from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from numpy import insert
from models import ProjectModel, ChunkModel
from models import ResponseSignal
import logging
from .schemes import SearchRequest, PushRequest
from tqdm.auto import tqdm
from controllers import NLPController
import asyncio


nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1","nlp"],
    )

@nlp_router.post("/index/push/{project_id}")
async def push_to_index(project_id: int, request: Request, push_request: PushRequest):

    project_model = await ProjectModel.create_instance(
        db_client = request.app.db_client
        )

    chunk_model = await ChunkModel.create_instance(
        db_client = request.app.db_client
        )

    project= await project_model.get_project_or_create_one(
        project_id=project_id
        )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": ResponseSignal.PROJECT_NOT_FOUND.value
                }
        )
    

    nlp_controller = NLPController(
        vector_db_client = request.app.vector_db_client,
        embedding_client = request.app.embedding_client,
        generation_client = request.app.generation_client,
        template_parser = request.app.template_parser
        )

    has_records = True
    page_no = 1
    idx = 0
    inserted_items_count = 0

     # create collection if not exists
    collection_name = nlp_controller.create_collection_name(project_id=project.project_id)

    _ = await request.app.vector_db_client.create_collection(
        collection_name=collection_name,
        embedding_size=request.app.embedding_client.embedding_size,
        do_reset=push_request.do_reset,
    )

    # setup batching
    total_chunks_count = await chunk_model.get_total_chunks_count(project_id=project.project_id)
    pbar = tqdm(total=total_chunks_count, desc="Vector Indexing", position=0)

    while has_records:
        page_chunks = await chunk_model.get_project_chunks(project_id=project.project_id, page_no=page_no)

        if len(page_chunks):
            page_no += 1

        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunks_ids =  [ c.chunk_id for c in page_chunks ]
        idx+=len(page_chunks)

        is_inserted = await nlp_controller.index_into_vector_db(project=project,
                                                chunks=page_chunks,
                                                chunks_ids=chunks_ids)

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
                    }
            )

        pbar.update(len(page_chunks))
        inserted_items_count += len(page_chunks)
        await asyncio.sleep(4)

    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
                "inserted_count": len(page_chunks)
                }
        )



@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: int):

    project_model = await ProjectModel.create_instance(
        db_client = request.app.db_client
        )

    project= await project_model.get_project_or_create_one(
        project_id=project_id
        )

    nlp_controller = NLPController(
        vector_db_client = request.app.vector_db_client,
        embedding_client = request.app.embedding_client,
        generation_client = request.app.generation_client,
        template_parser = request.app.template_parser
        )

    collection_info = await nlp_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
                content={
                    "signal": ResponseSignal.VECOTRDB_COLLECTON_RETRIEVED.value,
                    "collection_info": collection_info
                    }
            )


@nlp_router.post("/index/search/{project_id}")
async def answer(request: Request, project_id: int, search_request: SearchRequest):

    
    project_model = await ProjectModel.create_instance(
        db_client = request.app.db_client
        )

    project= await project_model.get_project_or_create_one(
        project_id=project_id
        )

    nlp_controller = NLPController(
        vector_db_client = request.app.vector_db_client,
        embedding_client = request.app.embedding_client,
        generation_client = request.app.generation_client,
        template_parser = request.app.template_parser
        )

    results = await nlp_controller.search_vector_db_collection(project=project,
                                                         query_text = search_request.text,
                                                         top_k = search_request.top_k
                                )
    
    if not results:
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.VECTORDB_SEARCH_ERROR.value
                }
        )

    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            "results": results,
        }
    )


@nlp_router.post("/index/answer/{project_id}")
async def answer(request: Request, project_id: int, search_request: SearchRequest):

    project_model = await ProjectModel.create_instance(
        db_client = request.app.db_client
    )

    project= await project_model.get_project_or_create_one(
        project_id=project_id
    )

    nlp_controller = NLPController(
    vector_db_client = request.app.vector_db_client,    
    embedding_client = request.app.embedding_client,
    generation_client = request.app.generation_client,
    template_parser = request.app.template_parser
    )

    answer, full_prompt, chat_history = await nlp_controller.answer_rag_question(
        project=project,
        query_text=search_request.text,
        top_k=search_request.top_k
    )


    if not answer:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.RAG_ANSWER_ERROR.value
                }
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history
            }
    )