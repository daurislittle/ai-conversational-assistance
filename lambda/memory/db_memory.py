from typing import List, Dict, Optional
import logging
import boto3
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

db = boto3.resource('dynamodb')
table = db.Table('ConversationalSessionTable')

MAX_MESSAGES = 20
MAX_TOKENS = 1000
TTL_SECONDS = 5000

def save_message(session_id: str, role: str, message: str, tokens: int = 0) -> None:
    timestamp = datetime.now(timezone.utc)
    
    ttl = int(timestamp.timestamp()) + TTL_SECONDS
    
    item = {
        "session_id": session_id,
        "role": role,
        "message": message,
        "tokens": tokens,
        "timestamp": timestamp.isoformat(),
        "ttl": ttl
    }
    
    try:
        table.put_item(Item=item)
        logger.info(f"Saved {role} message to DynamoDB session {session_id}")
    except Exception as e:
        logger.error(f"Error saving message to DynamoDB: {e}")
        raise
    
def get_messages(session_id: str) -> List[Dict]:
        
    try:
        pass
    except Exception as e:
        logger.error(f"Error retrieving messages from DynamoDB: {e}")
        raise []
        
        
def trim_messages(messages: List[Dict], max_tokens: int, max_messages: int) -> List[Dict]:
    
    if len(messages) > max_messages:
        pass
    
    total_tokens = 0
    kept_msgs = []
    
    for msg in reversed(messages):
        pass
    
    return kept_msgs

def expected_format_llm(messages: List[Dict]) -> List[Dict]:
    
    return [
        {"role": msg["role"], "content": msg["message"]} for msg in messages
        ]
        
