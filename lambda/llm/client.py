import os
import json
import time
import logging
import boto3
from typing import List, Dict, Optional


logging = logging.getLogger(__name__)

_secret_cache: Dict[str, str] = {}

def get_secret(secret_name: str) -> str:
    if secret_name in _secret_cache:
        logging.debug(f"Fetching secret {secret_name} from cache")
        return _secret_cache[secret_name]
    
    client = boto3.client("secretsmanager")
    
    logging.debug(f"Fetching secret {secret_name} from AWS Secrets Manager")
    response = client.get_secret_value(SecretId=secret_name)
    
    raw = response.get("SecretString", "{}")
    secret = json.loads(raw)
    
    api_key = secret.get("api_key")
    if not api_key:
        raise ConfigurationError(f"API key not found in secret {secret_name}")
    
    _secret_cache[secret_name] = api_key
    logging.info(f"Secret {secret_name} fetched successfully")
    return api_key

def _call_bedrock(messages: List[Dict]) -> str:
    
    model_id = os.getenv("BEDROCK_MODEL_ID", "default-model")
    max_tokens = int(os.getenv("BEDROCK_MAX_TOKENS", "400"))
    temperature = float(os.getenv("BEDROCK_TEMPERATURE", "0.7"))
    
    bedrock_region = os.getenv("BEDROCK_REGION", "us-east-1")
    system_blocks = []
    conversation_blocks = []
    
    for msg in messages:
        if msg["role"] == "system":
            system_blocks.append({
                "text": msg["content"]
            })
        else:
            conversation_blocks.append({
                "role": msg["role"],
                "content": [{"text": msg["content"]}]
            })
            
    bedrock_client = boto3.client("bedrock-runtime", region_name=bedrock_region)
    
    #logging.info(f"Calling Bedrock model {model_id} with {len(messages)} messages")
    
    request_kwargs = {
        "modelId": model_id,
        "messages": conversation_blocks,
        "inferenceConfiguration": {
            "maxTokens": max_tokens,
            "temperature": temperature
        }
    }
    
    if system_blocks:
        request_kwargs["system"] = system_blocks
        
    response = bedrock_client.invoke_model(**request_kwargs)
    
    output = response.get("output", [])
    output_message = output.get("message", {})
    content_blocks = output_message.get("content", [])
    
    text_parts = [block.get("text", "") for block in content_blocks]
    content = " ".join(text_parts)
    return content
    
    
def call_llm_with_retry(messages: List[Dict[str, str]], max_retries: int = 3, delay: int = 2) -> str:
    pass

def _call_llm(messages: List[Dict[str, str]]) -> str:
    pass

class LLMError(Exception):
    pass

class RateLimitErr(LLMError):
    pass

class TransientErr(LLMError):
    pass

class InvalidResponseErr(LLMError):
    pass

class ConfigurationError(LLMError):
    pass