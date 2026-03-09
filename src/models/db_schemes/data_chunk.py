from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId


class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_project_id: ObjectId
    chunk_order: int = Field(..., gt=0)



    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
                             
                             
                  