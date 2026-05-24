from ..LLMInterface import LLMInterface
from ..LLMEnums import CohereEnums, DocumentTypeQuery
import cohere
import logging

class CohereProvider(LLMInterface):

    def __init__(self,api_key:str,
                 default_input_max_characters: int=1000,
                 default_generation_max_output: int=1000,
                 default_generation_temperature: float=0.1):
    
        self.api_key = api_key
        
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output = default_generation_max_output
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key= self.api_key)

        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size


    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int=None, temperature: float = None):
        if not self.client:
            self.logger.error("Cohere client was not set")
            return None
        
        if not self.generation_model_id:
            self.logger.error("generation model for Cohere was not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output
        temperature = temperature if temperature else self.default_generation_temperature
        
        chat_history.append(self.construct_prompt(
            prompt = prompt,
            role = CohereEnums.USER.value
        ))


        response = self.client.chat(
            model = self.generation_model_id,
            messages= chat_history,
            max_tokens= max_output_tokens,
            temperature= temperature
        )

        if not response or not response.message or not response.message.content or not response.message.content[0].text:
            self.logger.error("Error while generating text using Cohere")
            return None
        
        return response.message.content[0].text

    def embed_text(self, text: str, document_type: str= None):
        
        if not self.client:
            self.logger.error("Cohere client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("embedding model with Cohere was not set")
            return None
        
        input_type = CohereEnums.DOCUMENT.value
        if document_type == DocumentTypeQuery.QUERY.value:
            input_type = CohereEnums.QUERY.value
        
        response = self.client.embed(
        model=self.embedding_model_id,
        texts=[self.process_text(text)],
        input_type = input_type,
        embedding_type = ["float"]
        ) 
        
        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("error while embedding text with Cohere")
            return None
        
        return response.embeddings.float[0]
    

    def construct_prompt(self, prompt: str, role: str):  
        return{
            "role": role,
            "content": self.process_text(prompt)
        }
    
    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()
