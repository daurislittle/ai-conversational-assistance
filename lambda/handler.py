import json
import logging
import os 
import boto3
import xray_recorder
import patch_all

patch_all()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from memory.db_memory import (save_message, get_messages,expected_format_llm, trim_messages)

from llm.client import call_llm_with_retry
from llm.prompt_builder import build_prompt
from utils.token_counter import count_tokens
from utils.validators import validate_request

def lambda_handler(event, context):
    
    with xray_recorder.in_segment('chat-handler'):
        
        try:
            body = parse_request(event)
            
            validate_request(body)
            
            session_id = body.get("session_id")
            usr_msg = body.get("message").strip()
            
            logger.info(json.dumps({
                "session_id": session_id, 
                "message": len(usr_msg),
                "event": "request_recieved"
                }))
            
            with xray_recorder.in_subsegment('load-memory'):
                raw_msgs = get_messages(session_id)
                message_trimmed = trim_messages(raw_msgs)
                history = expected_format_llm(message_trimmed)
                
                logger.info(json.dumps({
                    "session_id": session_id, 
                    "total_messages": len(raw_msgs),
                    "trimmed_messages": len(message_trimmed),
                    "event": "memory_loaded"
                    }))
                
            with xray_recorder.in_subsegment('build-prompt'):
                msgs = build_prompt(
                    history=history,
                    user_message=usr_msg,
                    system_message=get_system_prompt()
                )
                
                total_tokens = count_tokens(msgs)
                
                logger.info(json.dumps({
                    "total_tokens": total_tokens,
                    "event": "prompt_built"
                    }))
                
            with xray_recorder.in_subsegment('llm-call'):
                ai_msg = call_llm_with_retry(msgs)
                
                logger.info(json.dumps({
                    "event": "llm_response_completed",
                    "response_length": len(ai_msg)
                }))
            with xray_recorder.in_subsegment('save-memory'):
                usr_token = count_tokens([{"role": "user", "content": usr_msg}])
                ai_token = count_tokens([{"role": "assistant", "content": ai_msg}])
                
                save_message(session_id, "user", usr_msg, usr_token)
                save_message(session_id, "assistant", ai_msg, ai_token)
            
            return build_response({"response": ai_msg}, 200)
            
        except ValueError as ve:
            logger.error(f"ValueError: {ve}")
            return build_response({"error": str(ve)}, 400)
        except TimeoutError as te:
            logger.error(f"LLM TimeoutError: {te}")
            return build_response({"error": "The AI is taking too long to respond. Please try again."}, 504)
        except Exception as e:
            logger.error(f"Unhandled exception: {e}")
            return build_response({"error": "Something went wrong. Our team has been notified."}, 500)
        
def parse_request(event) -> dict:
    
    return {}

def get_system_prompt() -> str:
    pass

def build_response(request: dict, status_code: int) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(request)
    }

