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
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from utils.metrics import setup_metrics

app = FastAPI()

# Setup Prometheus metrics
setup_metrics(app)

async def startup_span():
    settings = get_settings()

    # create async engine for PostgreSQL
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    app.db_engine = create_async_engine(postgres_conn)

    app.db_client= sessionmaker(app.db_engine, class_=AsyncSession, expire_on_commit=False)

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
    vector_db_factory = VectorDBFactory(settings, db_client=app.db_client)

    app.vector_db_client = vector_db_factory.create(
    provider=settings.VECTOR_DB_BACKEND
    )
    await app.vector_db_client.connect()

    app.template_parser = TemplateParser(language = settings.PRIMARY_LANG, default_language = settings.DEFAULT_LANG)


async def shutdown_span():
    app.db_engine.dispose()
    app.vector_db_client.disconnect()


app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
