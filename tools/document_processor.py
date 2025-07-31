from pydantic import BaseModel, Field
from aparavi_dtc_sdk import AparaviClient
import sys
from tools.helper import process_response
from utils.path_utils import PathUtils

class DocumentResponse(BaseModel):
    """Response from document processing."""
    text: str = Field(..., description="Extracted text from the document")
    status: str = Field(..., description="Processing status")

class DocumentProcessor:
    """Document processing tool using Aparavi API."""

    def __init__(self, client: AparaviClient = None):
        """Initialize the document processor.

        Args:
            client: Initialized AparaviClient instance to use for API calls
        """
        self.client = client

    def SDK_Document_Processor(self, file_path: str) -> DocumentResponse:
        """Test using the Aparavi DTC SDK for document parsing.

        Args:
            file_path (str): Path to the document to parse

        Returns:
            LlamaParseResponse: Parsed document information
        """
        try:
            path = PathUtils.get_resource_path("resources/pipelines/simpleparser.json")

            # Execute pipeline using SDK
            response = self.client.execute_pipeline_workflow(
                pipeline=str(path),
                file_glob=file_path
            )

            # Process response using helper
            if response and len(response) > 0:
                result = process_response(response[0])
                print(f"Result: {result}", file=sys.stderr)

                return DocumentResponse(
                    text=result,
                    status="completed"
                )

        except Exception as e:
            print(f"SDK pipeline execution error: {e}", file=sys.stderr)
            return DocumentResponse(
                text="",
                status="failed"
            )
