from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum
import cohere
import logging
import time
from cohere.errors import TooManyRequestsError
from typing import List,Union

class CoHereProvider(LLMInterface):

    def __init__(self, api_key: str,
                       default_input_max_characters: int=1000,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):
        
        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key=self.api_key)

        self.enums = CoHereEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None, max_retries: int = 3):

        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere was not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        for attempt in range(max_retries):
            try:
                response = self.client.chat(
                    model = self.generation_model_id,
                    chat_history = chat_history,
                    message = self.process_text(prompt),
                    temperature = temperature,
                    max_tokens = max_output_tokens
                )

                if not response or not response.text:
                    self.logger.error("Error while generating text with CoHere")
                    return None
                
                return response.text
                
            except TooManyRequestsError as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 60  # Exponential backoff: 1min, 2min, 4min
                    self.logger.warning(f"Rate limit hit. Retrying in {wait_time} seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Max retries exceeded for CoHere generation. Rate limit error: {e}")
                    raise e
            except Exception as e:
                self.logger.error(f"Error while generating text with CoHere: {e}")
                return None
    
    def embed_text(self, text: Union[str,List[str]], document_type: str = None, max_retries: int = 3):
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        if isinstance(text,str):
            text=[text]
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None
        
        input_type = CoHereEnums.DOCUMENT
        if document_type == DocumentTypeEnum.QUERY:
            input_type = CoHereEnums.QUERY

        for attempt in range(max_retries):
            try:
                response = self.client.embed(
                    model = self.embedding_model_id,
                    texts = [self.process_text(t) for t in text],
                    input_type = input_type,
                    embedding_types=['float'],
                )

                if not response or not response.embeddings or not response.embeddings.float:
                    self.logger.error("Error while embedding text with CoHere")
                    return None
                return [f for f in response.embeddings.float]
                #return response.embeddings.float[0]
                
            except TooManyRequestsError as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 60  # Exponential backoff: 1min, 2min, 4min
                    self.logger.warning(f"Rate limit hit. Retrying in {wait_time} seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Max retries exceeded for CoHere embedding. Rate limit error: {e}")
                    raise e
            except Exception as e:
                self.logger.error(f"Error while embedding text with CoHere: {e}")
                return None
    
    def embed_batch(self, texts: list, document_type: str = None, max_retries: int = 3):
        """
        Embed multiple texts in a single API call to reduce rate limit issues.
        CoHere supports up to 96 texts per batch.
        """
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None
        
        if not texts:
            return []
        
        # Process texts and limit batch size to 96 (CoHere's limit)
        processed_texts = [self.process_text(text) for text in texts[:96]]
        
        input_type = CoHereEnums.DOCUMENT
        if document_type == DocumentTypeEnum.QUERY:
            input_type = CoHereEnums.QUERY

        for attempt in range(max_retries):
            try:
                response = self.client.embed(
                    model = self.embedding_model_id,
                    texts = processed_texts,
                    input_type = input_type,
                    embedding_types=['float'],
                )

                if not response or not response.embeddings or not response.embeddings.float:
                    self.logger.error("Error while batch embedding texts with CoHere")
                    return None
                
                return response.embeddings.float
                
            except TooManyRequestsError as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 60  # Exponential backoff: 1min, 2min, 4min
                    self.logger.warning(f"Rate limit hit during batch embedding. Retrying in {wait_time} seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Max retries exceeded for CoHere batch embedding. Rate limit error: {e}")
                    raise e
            except Exception as e:
                self.logger.error(f"Error while batch embedding texts with CoHere: {e}")
                return None
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": prompt
        }