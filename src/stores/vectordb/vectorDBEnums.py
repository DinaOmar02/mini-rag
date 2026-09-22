from enum import Enum


class VectorDBEnums(Enum):
    QDRANT = "QDRANT"
    PGVECTOR = "PGVECTOR"

class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"

class PGVectorTableschemaEnums(Enum):
    ID = "id"
    VECTOR = "vector"
    TEXT = "text"
    METADATA = "metadata"
    _PREFIX = "pgvector_"
    CHUNK_ID = "chunk_id"

class PGVectorDistanceMethodEnums(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops"

class PGVectorIndexTypeEnums(Enum):
    IVFFLAT = "ivfflat"
    HNSW = "hnsw"
