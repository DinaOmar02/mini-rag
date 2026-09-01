from fastapi import FastAPI
from routes import base, data, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.vectorDBFactory import VectorDBFactory
from stores.llm.templates.template_parser import TemplateParser


#from dotenv import load_dotenv  replaced by helpers/config.py
#load_dotenv(".env")   replaced by helpers/config.py

import os
from routes import base, data, nlp

app = FastAPI()


async def startup_span():
    settings = get_settings()
    app.mongo_connect= AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client= app.mongo_connect[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMProviderFactory(settings)

    # generation client
    app.generation_client = llm_provider_factory.create(provider = settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider = settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, 
                                                embedding_size = settings.EMBEDDING_MODEL_SIZE
    )

    # vector db client
    vector_db_factory = VectorDBFactory(settings)

    app.vector_db_client = vector_db_factory.create(
    provider=settings.VECTOR_DB_BACKEND
    )
    app.vector_db_client.connect()

    app.template_parser = TemplateParser(language = settings.PRIMARY_LANG, default_language = settings.DEFAULT_LANG)


async def shutdown_span():
    app.mongo_connect.close()
    app.vector_db_client.disconnect()


app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
