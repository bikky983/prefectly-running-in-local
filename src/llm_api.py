"""
LLM API integration module for Nepali News Summarizer.
Provides text summarization using DeepSeek API with retry logic and error handling.
"""

import asyncio
import time
from typing import Dict, Optional, Any
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from loguru import logger

from .config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_URL,
    LLM_REQUEST_TIMEOUT,
    LLM_MAX_RETRIES,
    LLM_RETRY_DELAY,
    RATE_LIMIT_CALLS_PER_MINUTE,
    validate_api_configuration,
    get_api_headers,
    get_summarization_request_body
)


class LLMAPIError(Exception):
    """Custom exception for LLM API related errors."""
    pass


class RateLimitError(LLMAPIError):
    """Exception raised when rate limit is exceeded."""
    pass


class APIKeyError(LLMAPIError):
    """Exception raised when API key is missing or invalid."""
    pass


class RateLimiter:
    """Simple rate limiter to prevent API abuse."""
    
    def __init__(self, calls_per_minute: int = RATE_LIMIT_CALLS_PER_MINUTE):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]
        
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, waiting {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
        
        self.calls.append(now)


# Global rate limiter instance
rate_limiter = RateLimiter()


async def _make_api_request_single(
    client: httpx.AsyncClient, 
    api_url: str,
    request_body: dict,
    headers: dict,
    model_name: str
) -> dict:
    """
    Make a single API request to an LLM endpoint.
    
    Args:
        client: HTTP client instance
        api_url: API endpoint URL
        request_body: Request payload
        headers: Request headers
        model_name: Name of the model (for logging)
    
    Returns:
        dict: API response
    
    Raises:
        LLMAPIError: If API request fails
        RateLimitError: If rate limit is exceeded
    """
    try:
        response = await client.post(
            api_url,
            json=request_body,
            headers=headers,
            timeout=LLM_REQUEST_TIMEOUT
        )
        
        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get("retry-after", 10))
            logger.warning(f"  Rate limited (429) for {model_name}, retry after {retry_after}s")
            raise RateLimitError(f"Rate limited, retry after {retry_after} seconds")
        
        # Handle insufficient credits
        if response.status_code == 402:
            logger.warning(f"  Model {model_name} requires credits (402)")
            raise LLMAPIError(f"Insufficient credits for {model_name}")
        
        # Handle model not found
        if response.status_code == 404:
            logger.warning(f"  Model {model_name} not found (404)")
            raise LLMAPIError(f"Model {model_name} not available")
        
        # Handle other HTTP errors
        response.raise_for_status()
        
        return response.json()
        
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text[:100]}"
        logger.error(f"  {error_msg}")
        raise LLMAPIError(error_msg)
    
    except httpx.RequestError as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(f"  {error_msg}")
        raise LLMAPIError(error_msg)


async def _make_api_request(client: httpx.AsyncClient, request_body: dict) -> dict:
    """
    Make API request with automatic fallback to multiple free models.
    Tries DeepSeek first, then falls back to other free OpenRouter models.
    
    Args:
        client: HTTP client instance
        request_body: Request payload
    
    Returns:
        dict: API response
    
    Raises:
        LLMAPIError: If all models fail after retries
    """
    headers = get_api_headers()
    
    # Define models to try in order (primary + fallbacks)
    models_to_try = [
        {
            "url": DEEPSEEK_API_URL,
            "model": request_body.get("model", "deepseek-chat"),
            "name": "DeepSeek (Primary)",
            "headers": headers
        },
        {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "model": "meta-llama/llama-3.2-3b-instruct:free",
            "name": "Llama 3.2 3B (FREE)",
            "headers": {
                **headers,
                "HTTP-Referer": "https://github.com",
                "X-Title": "Nepali News Summarizer"
            }
        },
        {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "model": "google/gemini-2.0-flash-exp:free",
            "name": "Gemini 2.0 Flash (FREE)",
            "headers": {
                **headers,
                "HTTP-Referer": "https://github.com",
                "X-Title": "Nepali News Summarizer"
            }
        },
        {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "model": "qwen/qwen-2-7b-instruct:free",
            "name": "Qwen 2 7B (FREE)",
            "headers": {
                **headers,
                "HTTP-Referer": "https://github.com",
                "X-Title": "Nepali News Summarizer"
            }
        }
    ]
    
    # Try each model with retry logic
    for model_config in models_to_try:
        logger.info(f"Trying model: {model_config['name']}")
        
        # Update request body with current model
        current_request = {**request_body, "model": model_config["model"]}
        
        # Try this model with retries
        max_retries = 2
        for attempt in range(max_retries):
            try:
                logger.info(f"  Attempt {attempt + 1}/{max_retries}...")
                
                response = await _make_api_request_single(
                    client,
                    model_config["url"],
                    current_request,
                    model_config["headers"],
                    model_config["name"]
                )
                
                logger.info(f"✓ Successfully got response from {model_config['name']}")
                return response
                
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)  # 5s, 10s
                    logger.warning(f"  Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"  Max retries reached for {model_config['name']}, trying next model...")
                    break
                    
            except LLMAPIError as e:
                # For 402/404 errors, immediately try next model
                if "402" in str(e) or "404" in str(e) or "credits" in str(e).lower():
                    logger.warning(f"  Skipping {model_config['name']}, trying next model...")
                    break
                # For other errors, retry
                elif attempt < max_retries - 1:
                    logger.warning(f"  Retrying after error...")
                    await asyncio.sleep(2)
                    continue
                else:
                    logger.warning(f"  Max retries reached for {model_config['name']}, trying next model...")
                    break
                    
            except Exception as e:
                logger.error(f"  Unexpected error with {model_config['name']}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                    continue
                else:
                    break
    
    # If we get here, all models failed
    error_msg = "All AI models failed to generate summary (tried DeepSeek + 3 free fallback models)"
    logger.error(f"✗ {error_msg}")
    raise LLMAPIError(error_msg)


def _extract_summary_from_response(api_response: dict) -> str:
    """
    Extract summary text from API response.
    
    Args:
        api_response: Raw API response
    
    Returns:
        str: Extracted summary text
    
    Raises:
        LLMAPIError: If response format is unexpected
    """
    try:
        choices = api_response.get("choices", [])
        if not choices:
            raise LLMAPIError("No choices in API response")
        
        message = choices[0].get("message", {})
        content = message.get("content", "").strip()
        
        if not content:
            raise LLMAPIError("Empty content in API response")
        
        return content
        
    except (KeyError, IndexError, AttributeError) as e:
        error_msg = f"Unexpected API response format: {str(e)}"
        logger.error(f"{error_msg}. Response: {api_response}")
        raise LLMAPIError(error_msg)


async def summarize_text_async(text: str, title: str = "", language: str = "ne") -> Dict[str, Any]:
    """
    Asynchronously summarize text using DeepSeek API.
    
    Args:
        text: Text to summarize (Nepali news article content)
        language: Language code ("ne" for Nepali, "en" for English)
    
    Returns:
        dict: {
            'summary': str,           # Generated summary
            'raw_api_response': dict, # Full API response
            'success': bool,          # Whether summarization succeeded
            'error': str,            # Error message if failed
            'metadata': dict         # Additional metadata
        }
    
    Raises:
        APIKeyError: If API key is missing or invalid
        LLMAPIError: If API request fails after retries
    """
    # Validate API configuration
    is_valid, error_msg = validate_api_configuration()
    if not is_valid:
        logger.error(f"API configuration error: {error_msg}")
        raise APIKeyError(error_msg)
    
    # Validate input
    if not text or not text.strip():
        return {
            'summary': '',
            'raw_api_response': {},
            'success': False,
            'error': 'Empty text provided',
            'metadata': {'language': language, 'text_length': 0}
        }
    
    # Apply rate limiting
    rate_limiter.wait_if_needed()
    
    # Prepare request
    request_body = get_summarization_request_body(text, title, language)
    
    logger.info(f"Summarizing text ({len(text)} chars) in language: {language}")
    
    try:
        async with httpx.AsyncClient() as client:
            api_response = await _make_api_request(client, request_body)
            
            # Extract summary
            summary = _extract_summary_from_response(api_response)
            
            logger.info(f"Successfully generated summary ({len(summary)} chars)")
            
            return {
                'summary': summary,
                'raw_api_response': api_response,
                'success': True,
                'error': None,
                'metadata': {
                    'language': language,
                    'text_length': len(text),
                    'summary_length': len(summary),
                    'model_used': request_body.get('model'),
                    'tokens_used': api_response.get('usage', {}).get('total_tokens', 0)
                }
            }
            
    except (APIKeyError, LLMAPIError) as e:
        logger.error(f"LLM API error: {str(e)}")
        return {
            'summary': '',
            'raw_api_response': {},
            'success': False,
            'error': str(e),
            'metadata': {'language': language, 'text_length': len(text)}
        }
    
    except Exception as e:
        logger.error(f"Unexpected error during summarization: {str(e)}")
        return {
            'summary': '',
            'raw_api_response': {},
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'metadata': {'language': language, 'text_length': len(text)}
        }


def summarize_text(text: str, title: str = "", language: str = "ne") -> Dict[str, Any]:
    """
    Synchronous wrapper for text summarization.
    
    Args:
        text: Text to summarize (Nepali news article content)
        language: Language code ("ne" for Nepali, "en" for English)
    
    Returns:
        dict: Same format as summarize_text_async
    
    Example:
        >>> result = summarize_text("काठमाडौं । आजको मौसम...")
        >>> if result['success']:
        ...     print(f"Summary: {result['summary']}")
        ... else:
        ...     print(f"Error: {result['error']}")
    """
    try:
        # Run async function in event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an event loop, create a new one
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, summarize_text_async(text, title, language))
                return future.result()
        else:
            return loop.run_until_complete(summarize_text_async(text, title, language))
    except Exception as e:
        return asyncio.run(summarize_text_async(text, title, language))


# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.llm_api <text_to_summarize>")
        print("Example: python -m src.llm_api 'नेपाली समाचार...'")
        sys.exit(1)
    
    test_text = sys.argv[1]
    test_title = sys.argv[2] if len(sys.argv) > 2 else ""
    
    print(f"Summarizing: {test_text[:100]}...")
    
    result = summarize_text(test_text, test_title)
    
    if result['success']:
        print(f"Summary: {result['summary']}")
        print(f"Metadata: {result['metadata']}")
    else:
        print(f"Error: {result['error']}")
