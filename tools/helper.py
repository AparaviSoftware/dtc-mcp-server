"""Helper functions for processing responses and common operations."""

from typing import Optional, Dict, Any
import sys

def process_response(response: Dict[str, Any]) -> Optional[str]:
    """Process an Aparavi client response and extract the text content.
    
    Args:
        response (Dict[str, Any]): The response from Aparavi client
        
    Returns:
        Optional[str]: The extracted text if found, None otherwise
        
    Example response structure:
    {
        "status": "OK",
        "data": {
            "objects": {
                "some-uuid": {
                    "text": ["actual text content here"]
                }
            }
        }
    }
    """
    try:
        # Check response status
        if response.get("status") != "OK":
            print(f"Response status not OK: {response.get('status')}", file=sys.stderr)
            return None
            
        # Navigate through response structure
        data = response.get("data", {})
        objects = data.get("objects", {})
        
        # No objects found
        if not objects:
            print("No objects found in response", file=sys.stderr)
            return None
            
        # Get first object (there's usually only one)
        first_object_id = next(iter(objects))
        first_object = objects[first_object_id]
        
        # Extract text
        text_list = first_object.get("text", [])
        if not text_list:
            print("No text found in object", file=sys.stderr)
            return None
            
        # Return first text element (usually there's only one)
        return text_list[0] if isinstance(text_list, list) else text_list
        
    except Exception as e:
        print(f"Error processing response: {e}", file=sys.stderr)
        return None
