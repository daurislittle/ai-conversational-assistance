import json
import logging
import os 
import boto3
import xray_recorder
import patch_all

patch_all()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

import memory.db_memory

from llm.client import call_llm_with_retry
from llm.prompt_builder import build_prompt
from utils.token_counter import count_tokens
from utils.validators import validate_request

def lambda_handler(event, context):
    
    with xray_recorder.in_segment('chat-handler'):
        
        try:
            pass
        except ValueError as ve:
            pass
        except TimeoutError as te:
            pass
        except Exception as e:
            pass
        
def parse_request(event) -> dict:
    
    return {}

def get_system_prompt() -> str:
    pass

def build_response(request: dict, status_code: int) -> dict:
    pass

