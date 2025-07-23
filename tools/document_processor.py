"""Tool for processing documents through Aparavi API."""

from pathlib import Path
from pydantic import BaseModel, Field
import json
from integrations.aparavi.client import AparaviClient
from integrations.aparavi.exceptions import AparaviError

class DocumentRequest(BaseModel):
    """Request parameters for document processing."""
    file_path: str = Field(..., description="Path to the document file to process")
    type: str = Field(default="gpu", description="Type of processing to use (gpu or cpu)")

class DocumentResponse(BaseModel):
    """Response from document processing."""
    text: str = Field(..., description="Extracted text from the document")
    status: str = Field(..., description="Processing status")

class DocumentProcessor:
    """Document processing tool using Aparavi API."""
    
    def __init__(self, client: AparaviClient):
        """Initialize the document processor.
        
        Args:
            client: Initialized AparaviClient instance to use for API calls
        """
        self.client = client
        
        # Load pipeline configuration
        pipeline_config_path = "resources/pipelines/simpleparser.json"
        with open(pipeline_config_path, 'r') as f:
            pipeline_data = json.load(f)
            
        self.pipeline_config = {
            "pipeline": {
                "source": "webhook_1",
                "components": pipeline_data["components"]
            }
        }
    
    def process_document(self, request: DocumentRequest) -> DocumentResponse:
        """Process a document through Aparavi API and return extracted text.
        
        Args:
            request: Parameters containing the file path and processing type
            
        Returns:
            DocumentResponse: Extracted text and status
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            AparaviError: For API processing errors
        """
        # Validate file exists
        file_path = Path(request.file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Create task and wait for it to be ready
            task_token, ready_status = self.client.create_and_wait_for_task(
                pipeline=self.pipeline_config,
                name=f"Process {file_path.name}",
                type=request.type,
                max_retries=10,
                initial_delay=2.0,
                timeout=60.0
            )

            # Read and send file data
            with open(file_path, 'r') as f:  # Changed to text mode
                file_content = f.read()

            # Send file data
            result = self.client.post_to_webhook(
                token=task_token,
                data={
                    "content": file_content,  # Send raw content
                    "filename": file_path.name
                },
                type=request.type
            )

            # Extract text from the result
            if (result.get('status') == 'OK' and 
                result.get('data', {}).get('objects')):
                
                # Get the first object's text (there should only be one)
                first_object = next(iter(result['data']['objects'].values()))
                if first_object.get('text'):
                    # Get the raw text content
                    text_content = first_object['text'][0]
                    
                    # If it's JSON encoded, try to decode it
                    try:
                        import json
                        parsed = json.loads(text_content)
                        if isinstance(parsed, dict) and 'content' in parsed:
                            text_content = parsed['content']
                    except (json.JSONDecodeError, TypeError):
                        pass  # Use text as-is if not JSON
                        
                    return DocumentResponse(
                        text=text_content,
                        status="completed"
                    )

            raise AparaviError("No text content found in processing result")
            
        except Exception as e:
            # Clean up task on failure if we have a token
            if 'task_token' in locals():
                try:
                    self.client.end_task(task_token)
                except:
                    pass  # Ignore cleanup errors
            raise 