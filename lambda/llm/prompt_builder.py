from typing import List, Dict

def build_prompt(system_message: str, history: List[Dict], user_message: str) -> List[Dict[str, str]]:
    messages = []
    
    messages.append({
        "role": "user",
        "content": system_message
    })
    
    messages.extend(history)
    
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    return messages

def build_structured_prompt(system_message: str, history: List[Dict], user_message: str, output_schema: Dict) -> str:
    
    schema_instruction = """
    you must respond with valid JSON only. No markdown, no explanations, just JSON.
    
    ensure the output strictly follows this schema: {str(output_schema)}
    """
    
    enhanced_system_message = f"{system_message}\n{schema_instruction}"
    return build_prompt(enhanced_system_message, history, user_message)