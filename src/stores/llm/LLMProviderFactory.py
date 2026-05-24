from .LLMEnums import LLMEnums
from .providers import OpenAIProvider, CohereProvider

class LLMProviderFactory():

    def __init__(self, config):
        self.config = config

    def create(self, provider):

        if provider == LLMEnums.OPENAI.value:
            llm_provider = OpenAIProvider(
                api_key= self.config.OPENAI_API_KEY,
                default_input_max_characters= self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_max_output= self.config.DEFAULT_GENERATION_MAX_OUTPUT,
                default_generation_temperature= self.config.DEFAULT_GENERATION_TEMPERATURE
            )
            return llm_provider

        elif provider == LLMEnums.COHERE.value:
            llm_provider = CohereProvider(
                api_key= self.config.COHERE_API_KEY,
                default_input_max_characters= self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_max_output= self.config.DEFAULT_GENERATION_MAX_OUTPUT,
                default_generation_temperature= self.config.DEFAULT_GENERATION_TEMPERATURE
            )
            return llm_provider

        else:
            raise ValueError(f"Unsupported provider: {provider}")
