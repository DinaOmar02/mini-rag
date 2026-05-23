from enum import Enum
from xmlrpc.client import SYSTEM_ERROR

class LLMEnums(Enum):

    OPENAI = "OPENAI"
    COHERE = "COHERE"

class OpenAIEnums(Enum):

    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


