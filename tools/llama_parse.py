import sys
from pydantic import BaseModel, Field
from tools.helper import process_response
from aparavi_dtc_sdk import AparaviClient
from utils.path_utils import PathUtils

class LlamaParseClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key


class LlamaParseResponse(BaseModel):
    """Response from LlamaParse processing."""
    text: str = Field(..., description="Extracted text from the document")
    status: str = Field(..., description="Processing status")


class LLamaParse:
    """LLamaParse class for document parsing and processing.


    Attributes:
        aparavi_client: Client for Aparavi API interactions
        llama_client: Client for LlamaIndex API interactions
    """

    def __init__(self, aparavi_client: AparaviClient):
        """Initialize the LLamaParse instance.

        Args:
            aparavi_client (AparaviClient): Initialized Aparavi API client
        """
        self.aparavi_client = aparavi_client

    def SDK_LlamaParse(self, file_path: str) -> LlamaParseResponse:
        """Test using the Aparavi DTC SDK for document parsing.

        Args:
            file_path (str): Path to the document to parse

        Returns:
            LlamaParseResponse: Parsed document information
        """
        try:
            path = PathUtils.get_resource_path("resources/pipelines/llamaparsemaster.json")
            # Execute pipeline using SDK
            response = self.aparavi_client.execute_pipeline_workflow(
                pipeline=str(path),
                file_glob=file_path
            )

            # Process response using helper
            if response and len(response) > 0:
                result = process_response(response[0])
                print(f"Result: {result}", file=sys.stderr)

                return LlamaParseResponse(
                    text=result,
                    status="completed"
                )

        except Exception as e:
            print(f"SDK pipeline execution error: {e}", file=sys.stderr)
            return LlamaParseResponse(
                text="",
                status="failed"
            )
