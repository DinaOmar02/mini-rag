from http import client

from ..vectorDBInteface import VectorDBInterface
from ..vectorDBEnums import DistanceMethodEnums
from qdrant_client import QdrantClient, models
from typing import List
import logging
from models.db_schemes import RetrievedDocument

class QDrantDBProvider(VectorDBInterface):

    def __init__(self, db_path: str, distance_method: str = None):


        self.client = None
        self.db_path = db_path

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE

        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
        
        else:
            raise ValueError("Unsupported distance method")

        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        self.client = QdrantClient(path=self.db_path)
    
    def disconnect(self):
        self.client = None
    
    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self) -> List:
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name):
            self.client.delete_collection(collection_name=collection_name)

    def create_collection(self,
                           collection_name: str,
                             embedding_size: int,
                             do_reset: bool = False):
        if do_reset:
            self.delete_collection(collection_name)

        if not self.is_collection_existed(collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
                
            )
        
            return True
        
        return False

    
    def insert_one(self, collection_name: str,
                       text: str, vector: list,
                        metadata: dict=None,
                        record_id: str=None):
    
        
        if not self.is_collection_existed(collection_name):
            self.logger.error(f" Cant insert new record to collection not existed '{collection_name}")
            return False
        


        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        vector=vector,
                        id=[record_id],
                        payload={"text": text, "metadata": metadata}
                    )
                ]
            )

        except Exception as e:
            self.logger.error(f"Error occurred while uploading record to collection '{collection_name}': {e}")
            return False
           
        return True
    

    def insert_many(self, collection_name: str,
                     texts: list, vectors: list,
                       metadata: list=None,record_ids: list=None,
                         batch_size: int = 50):
        

        if metadata is None:
            metadata = [None] * len(texts)
        
        if record_ids is None:
            record_ids = list(range(0, len(texts)))


        if not self.is_collection_existed(collection_name):
            self.logger.error(f" Cant insert new records to collection not existed '{collection_name}")
            return False
        
        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]


            records = [
                models.Record(
                    id=batch_record_ids[x],
                    vector=batch_vectors[x],
                    payload={"text": batch_texts[x],
                              "metadata": batch_metadata[x]}
                )
                for x in range(len(batch_texts))
            ]

            try:

              _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=records
                )

            except Exception as e:
                self.logger.error(f"Error occurred while uploading batch of records to collection '{collection_name}': {e}")
                return False

        return True


    def search_by_vector(self, collection_name: str,
                         query_vector: list,
                         top_k: int = 5) -> list:
        
        if not self.is_collection_existed(collection_name):
            self.logger.error(f" Cant search in collection not existed '{collection_name}")
            return []
        
        results =  self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k
        )

        if not results or len(results) == 0:
            return None

        return [
            RetrievedDocument(**{
                "text": result.payload["text"],
                "score": result.score
            })
            for result in results
        ]

        


        




            
    
        

    

    


    

