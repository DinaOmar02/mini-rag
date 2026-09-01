from openai import chat

from models.db_schemes.data_chunk import DataChunk

from .BaseController import BaseController
from models.db_schemes import Project
from typing import List
from stores.llm import DocumentTypeEnum

import json

class NLPController(BaseController):

    def __init__(self, vector_db_client, embedding_client, generation_client, template_parser):
        super().__init__()

        self.vector_db_client = vector_db_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.template_parser = template_parser

    
    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    

    def reset_vector_db(self, project: Project):
        collection_name = self.create_collection_name(project.project_id)
        self.vector_db_client.delete_collection(collection_name = collection_name)

    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project.project_id)
        collection_info = self.vector_db_client.get_collection_info(collection_name = collection_name)

        return json.loads(
        json.dumps(collection_info, default=lambda x:x.__dict__)
        )

    
    def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                             chunks_ids:List[int], do_reset: bool = False):
        
        collection_name = self.create_collection_name(project.project_id)

        texts = [chunk.chunk_text for chunk in chunks]
        metadata = [chunk.chunk_metadata for chunk in chunks]

        vectors = [
            self.embedding_client.embed_text(text = text, document_type = DocumentTypeEnum.DOCUMENT.value)
                   
            for text in texts
                    ]

        _ = self.vector_db_client.create_collection(collection_name = collection_name,
                                                    embedding_size=self.embedding_client.embedding_size,
                                                    do_reset= do_reset)
        
        _ = self.vector_db_client.insert_many(collection_name = collection_name, texts = texts,
                                              metadata = metadata, vectors = vectors, record_ids = chunks_ids)

        return True
    

    def search_vector_db_collection(self, project: Project, query_text: str, top_k: int = 5):

        collection_name = self.create_collection_name(project.project_id)

        query_vector = self.embedding_client.embed_text(text = query_text, document_type = DocumentTypeEnum.QUERY.value)

        if not query_vector or len(query_vector) == 0:
            return False

        search_results = self.vector_db_client.search_by_vector(collection_name = collection_name,
                                                                query_vector=query_vector,
                                                                top_k=top_k)

        if not search_results or len(search_results) == 0:
            return False
        
        return json.loads(
        json.dumps(search_results, default=lambda x:x.__dict__)
        )

    

    def answer_rag_question(self, project: Project, query_text: str, top_k: int = 5):

        answer, full_prompt, chat_history = None, None, None

        #step1: reteive relevant documents from vector db
        search_results = self.search_vector_db_collection(
            project=project,
              query_text=query_text,
                top_k=top_k)

        if not search_results or len(search_results) == 0:
            return answer, full_prompt, chat_history

        #step2: construct LLM
        system_prompt = self.template_parser.get("rag", "system_prompt")

        documents_prompts = "\n".join([

            self.template_parser.get("rag", "document_prompt", {
                "doc_num": idx + 1,
                "chunk_text": doc["text"]
            })
            for idx, doc in enumerate(search_results)
        ])


        footer_prompt = self.template_parser.get("rag", "footer_prompt",
                                                 {"query" : query_text
                                                  })


        #chat history is system prompt
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value
            )
        ]

        full_prompt = "\n\n".join([documents_prompts, footer_prompt])

        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history,
        )

        return answer, full_prompt, chat_history
