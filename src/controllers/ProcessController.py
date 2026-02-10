from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from models import ProcessingEnum
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

# إعداد logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class ProcessController(BaseController):

    def __init__(self, project_id: str):
        super().__init__()

        self.proj_path = ProjectController().get_project_path(project_id=project_id)



    def get_file_extension(self, file_id: str):
       return os.path.splitext(file_id)[-1]
    

    def get_file_loader(self, file_id: str):

        file_path = os.path.join(self.proj_path, file_id)

        ext = self.get_file_extension(file_id= file_id)
        logger.info(f"Processing file with extension: {ext}")

        if ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path, encoding = "utf-8")
        elif ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding = "utf-8")
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
        
        

    def get_file_content(self, file_id: str):

        loader = self.get_file_loader(file_id=file_id)

        return loader.load()
    

    def get_content_chunks(self, content: list, chunk_size: int = 1000,  chunk_overlap: int = 0):    

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=0
            )

        file_content_text = [
            rec.page_content for rec in content
        ]

        file_content_metadata = [
            rec.metadata for rec in content
        ]
    

        chunks = text_splitter.create_documents(
            file_content_text,
              metadatas=file_content_metadata)
        
        return chunks
