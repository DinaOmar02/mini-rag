from models.db_schemes import DataChunk
from bson.objectid import ObjectId
from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from pymongo import InsertOne

class ChunkModel(BaseDataModel):

    def __init__(self, db_client= db_client):
        super.__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    
    async def create_chunk(self,chunk: DataChunk):
        result = await self.collection.insert_one(chunk.dict())
        chunk._id = result.inserted_id

        return chunk


    async def get_chunk(self, chunk_id:str):

        record = await self.collection.find_one({
            "_id": ObjectId(chunk_id)
        })

        if record is None :
            return None
        
        return DataChunk(**record)



    async def insert_many_chunks(self, chunks: list, batch_size: int=100):

        for i in range(0, len(chunk), batch_size):
            batch = chunks[i, i+batch_size]

            operations = [
                InsertOne(chunk.dict())
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)
        
        return len(chunks)

