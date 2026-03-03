from typing import List, Dict, Optional
import logging
import boto3
from datetime import datetime, timezone
import time

logger = logging.getLogger(__name__)

db = boto3.resource('dynamodb')
table = db.Table('ConversationalSessionTable')

MAX_MESSAGES = 20
MAX_TOKENS = 1000
TTL_SECONDS = 5000

def save_message(session_id: str, role: str, message: str, tokens: int = 0) -> None:
    """
    Save a message to the DynamoDB table for a given session.
    
    Args:
        session_id (str): The ID of the session.
        role (str): The role of the message sender (e.g., "user" or "assistant").
        message (str): The content of the message.
        tokens (int, optional): The number of tokens in the message. Defaults to 0.
    """
    timestamp = datetime.now(timezone.utc)
    
    ttl = int(timestamp.time()) + TTL_SECONDS
    
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
    """
    Retrieve all messages for a given session from the DynamoDB table.

    Args:
        session_id (str): The ID of the session.

    Returns:
        List[Dict]: A list of messages for the session, each represented as a dictionary.
    """
    try:
        res = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('session_id').eq(session_id), 
            ScanIndexForward=True
        )
        
        if res.get('Items'):
            logger.info(f"Retrieved {len(res['Items'])} messages from DynamoDB session {session_id}")

        return res.get('Items', [])
        
    except Exception as e:
        logger.error(f"Error retrieving messages from DynamoDB: {e}")
        raise []
        
        
def trim_messages(messages: List[Dict], max_tokens: int, max_messages: int) -> List[Dict]:
    """
    Trim the list of messages to ensure it does not exceed the maximum number of messages or tokens.

    Args:
        messages (List[Dict]): The list of messages to trim.
        max_tokens (int): The maximum allowed total tokens.
        max_messages (int): The maximum allowed number of messages.

    Returns:
        List[Dict]: The trimmed list of messages.
    """
    if len(messages) > max_messages:
        remove_count = len(messages) - max_messages
        messages = messages[-max_messages:]
        logger.info(f"Trimmed {remove_count} messages to maintain max_messages={max_messages}")
    
    total_tokens = 0
    kept_msgs = []
    
    for msg in reversed(messages):
        msg_tokens = msg.get("tokens", len(msg['content']) // 4)
        
        if total_tokens + msg_tokens > max_tokens:
            kept_msgs.insert(0, msg)
            total_tokens += msg_tokens
        else:
            logger.info(f"Token limit exceeded. Current total tokens: {total_tokens}. \n Dropping {len(msg) - len(kept_msgs)} messages")
            break
    
    return kept_msgs

def expected_format_llm(messages: List[Dict]) -> List[Dict]:
    """
    Format the messages for input to a language model.
    """
    return [
        {"role": msg["role"], "content": msg["message"]} for msg in messages
        ]
        
