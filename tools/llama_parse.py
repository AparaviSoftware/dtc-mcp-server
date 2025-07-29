"""LLamaParse module for document parsing using LlamaIndex.

This module provides functionality for parsing and processing documents using
LlamaIndex capabilities. It supports multiple parsing strategies and tools
while maintaining a consistent interface.
"""

from typing import Dict, Any
import json
import sys
from pathlib import Path
from pydantic import BaseModel, Field
from integrations.aparavi.client import AparaviClient
from tools.helper import process_response
# from aparavi_dtc_sdk import AparaviClient
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

    def __init__(self, aparavi_client: AparaviClient, llama_client: LlamaParseClient):
        """Initialize the LLamaParse instance.

        Args:
            aparavi_client (AparaviClient): Initialized Aparavi API client
            llama_client (LlamaParseClient): Initialized LlamaIndex API client
        """
        self.aparavi_client = aparavi_client
        self.llama_client = llama_client

    def insert_llama_key(self, pipeline_data: Dict) -> Dict:
        """Insert LlamaIndex API key into pipeline configuration.

        Args:
            pipeline_data: The pipeline configuration data

        Returns:
            Dict: Updated pipeline configuration with API key
        """
        # Find the llamaparse component
        for component in pipeline_data.get("components", []):
            if component.get("provider") == "llamaparse":
                config = component.setdefault("config", {})
                default_config = config.setdefault("default", {})
                default_config["api_key"] = self.llama_client.api_key
                break

        print(f"Pipeline data: {pipeline_data}", file=sys.stderr)
        return pipeline_data

    def llama_parse_document_parser(self, file_path: str) -> Dict[str, Any]:
        """Parse documents using LlamaIndex capabilities.

        Args:
            file_path (str): Path to the document to parse

        Returns:
            Dict[str, Any]: Parsed document information
        """

        # Load pipeline configuration from package resources
        pipeline_config_path = PathUtils.get_resource_path("resources/pipelines/llamaparse.json")

        if not PathUtils.is_file_exists(pipeline_config_path):
            raise FileNotFoundError(f"Pipeline configuration not found at: {pipeline_config_path}")

        with open(pipeline_config_path, 'r') as f:
            pipeline_data = json.load(f)

        # Insert LlamaIndex API key into pipeline configuration
        pipeline_data = self.insert_llama_key(pipeline_data)

        pipeline_config = {
            "pipeline": {
                "source": "webhook_1",
                "components": pipeline_data["components"]
            }
        }

        # Validate file exists
        file_path = PathUtils.normalize_path(file_path)
        if not PathUtils.is_file_exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"\nProcessing document: {file_path}", file=sys.stderr)

        # Create task and get server-assigned type
        task_token, task_type, _ = self.aparavi_client.create_and_wait_for_task(
            pipeline=pipeline_config,
            name=f"Process {file_path.name}",
            threads=None
        )

        # Send file to webhook using server-assigned type
        responses = self.aparavi_client.send_payload_to_webhook(
            token=task_token,
            task_type=task_type,
            file_glob=str(file_path)  # normalize_path already gives us absolute path
        )

        # Process response using helper
        if responses and len(responses) > 0:
            result = process_response(responses[0])
            print(f"Result: {result}", file=sys.stderr)

            return LlamaParseResponse(
                text=result,
                status="completed"
            )

        return LlamaParseResponse(
            text="",
            status="failed"
        )

    # def test_SDK_LlamaParse(self, file_path: str) -> LlamaParseResponse:
    #     """Test using the Aparavi DTC SDK for document parsing.

    #     Args:
    #         file_path (str): Path to the document to parse

    #     Returns:
    #         LlamaParseResponse: Parsed document information
    #     """
    #     try:
    #         # Execute pipeline using SDK
    #         result = self.aparavi_client.execute_pipeline_workflow(
    #             pipeline="./resources/pipelines/SDK_Test.json",
    #             file_glob="/Users/dylansavage/Desktop/mcp-server/tests/testdata/*.jpeg"
    #         )

    #         # SDK returns a list of results, one for each processed file
    #         if result and isinstance(result, list) and len(result) > 0:
    #             # Get the first result (since we're processing one file)
    #             first_result = result[0]

    #             # Debug log the result structure
    #             print(f"SDK Response structure: {json.dumps(first_result, indent=2)}", file=sys.stderr)

    #             # Extract text from the response
    #             if isinstance(first_result, dict):
    #                 data = first_result.get('data', {})
    #                 objects = data.get('objects', {})

    #                 # Get the first object's text
    #                 if objects:
    #                     first_object = next(iter(objects.values()))
    #                     text = first_object.get('text', [''])[0] if isinstance(first_object.get('text'), list) else ''

    #                     return LlamaParseResponse(
    #                         text=text,
    #                         status="completed"
    #                     )

    #         # If we couldn't extract text, return failure
    #         print(f"Could not extract text from result: {result}", file=sys.stderr)
    #         return LlamaParseResponse(
    #             text="",
    #             status="failed",
    #             prompt=None
    #         )

    #     except Exception as e:
    #         print(f"SDK pipeline execution error: {e}", file=sys.stderr)
    #         return LlamaParseResponse(
    #             text="",
    #             status="failed",
    #             prompt=None
    #         )
