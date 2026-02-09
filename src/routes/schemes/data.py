from pydentic import BaseModel

class ProcessRequest(BaseModel):

    file_id: str
    chunk_size = optional[int] = 20
    do_reset = optional[int] = 0
    
