from enum import Enum
from xmlrpc.client import SYSTEM_ERROR

class LLMEnums(Enum):

    OPENAI = "OPENAI"
    COHERE = "COHERE"

class OpenAIEnums(Enum):

    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"

class CohereEnums(Enum):

    SYSTEM = "SYSTEM"
    ASSISTANT = "CHATBOT"
    USER = "USER"

    DOCUMENT = "search_document"
    QUERY = "search_query"

class DocumentTypeEnum(Enum):

    DOCUMENT = "document"
    QUERY = "query"
