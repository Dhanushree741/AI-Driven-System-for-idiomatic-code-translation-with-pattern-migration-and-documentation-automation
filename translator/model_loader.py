import os
import logging
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)


class HFModelClient:
    """HuggingFace model client using the huggingface_hub InferenceClient."""
    
    def __init__(self, timeout=120):
        """
        Initialize the HuggingFace model client.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.api_token = os.getenv("HF_API_TOKEN")
        self.model_id = os.getenv("MODEL_ID")
        self.timeout = timeout
        self._client = None
        
        # Validate required environment variables
        if not self.api_token:
            raise ValueError("HF_API_TOKEN is missing!")
        
        if not self.model_id:
            raise ValueError("MODEL_ID is missing!")
    
    @property
    def client(self):
        """Lazy initialization of InferenceClient."""
        if self._client is None:
            try:
                self._client = InferenceClient(
                    self.model_id, 
                    token=self.api_token
                )
                logger.info(f"Model client initialized for model: {self.model_id}")
            except Exception as e:
                logger.error(f"Failed to initialize InferenceClient: {e}")
                raise ValueError(f"Failed to initialize model client: {e}")
        return self._client

    def generate(self, prompt):
        """
        Generate translation from the model.
        
        Args:
            prompt: The input prompt for translation
            
        Returns:
            Generated text from the model
            
        Raises:
            ValueError: If the prompt is invalid
            Exception: If the API call fails
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        try:
            # Use chat_completion for instruct models
            response = self.client.chat_completion(
                [{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800
            )
            
            result = response.choices[0].message.content
            
            logger.info("Generation completed successfully")
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Generation error: {error_msg}")
            
            # Provide more user-friendly error messages
            if "authentication" in error_msg.lower() or "401" in error_msg:
                raise Exception("Authentication failed. Check your HF_API_TOKEN.")
            elif "403" in error_msg or "forbidden" in error_msg.lower():
                raise Exception("Access forbidden. Check your model permissions.")
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                raise Exception("Rate limit exceeded. Please try again later.")
            elif "timeout" in error_msg.lower():
                raise Exception(f"Request timed out after {self.timeout} seconds. Try a shorter prompt.")
            else:
                raise Exception(f"Translation failed: {error_msg}")
