"""Tool for processing documents through Aparavi API."""

# from pathlib import Path
from pydantic import BaseModel, Field
import json
# from integrations.aparavi.client import AparaviClient
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

        # Load pipeline configuration from package resources
        pipeline_config_path = PathUtils.get_resource_path("resources/pipelines/simpleparser.json")

        if not PathUtils.is_file_exists(pipeline_config_path):
            raise FileNotFoundError(f"Pipeline configuration not found at: {pipeline_config_path}")

        with open(pipeline_config_path, 'r', encoding='utf-8') as f:
            pipeline_config = json.load(f)

        self.pipeline_config = {
            "pipeline": {
                "source": "webhook_1",
                "components": pipeline_config["components"]
            }
        }

    def process_document(self, file_path: str) -> DocumentResponse:
        """Process a document through Aparavi API and return extracted text.

        Args:
            file_path: Path to the document file to process

        Returns:
            DocumentResponse: Extracted text and status

        Raises:
            FileNotFoundError: If the file doesn't exist
            AparaviError: For API processing errors
        """
        # Validate file exists
        file_path = PathUtils.normalize_path(file_path)
        if not PathUtils.is_file_exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"\nProcessing document: {file_path}", file=sys.stderr)

        # Create task and get server-assigned type
        task_token, task_type, _ = self.client.create_and_wait_for_task(
            pipeline=self.pipeline_config,
            name=f"Process {file_path.name}",
            threads=None
        )

        # Send file to webhook using server-assigned type
        responses = self.client.send_payload_to_webhook(
            token=task_token,
            task_type=task_type,
            file_glob=str(file_path)  # normalize_path already gives us absolute path
        )

        if responses and len(responses) > 0:
            result = process_response(responses[0])
            print(f"Result: {result}", file=sys.stderr)

            return DocumentResponse(
                text=result,
                status="completed"
            )

        else:
            return DocumentResponse(
                text="",
                status="failed"
            )

    def SDK_Document_Processor(self, file_path: str) -> DocumentResponse:
        """Test using the Aparavi DTC SDK for document parsing.

        Args:
            file_path (str): Path to the document to parse

        Returns:
            LlamaParseResponse: Parsed document information
        """
        try:
            # Execute pipeline using SDK
            response = self.client.execute_pipeline_workflow(
                pipeline="./resources/pipelines/simpleparser.json",
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
