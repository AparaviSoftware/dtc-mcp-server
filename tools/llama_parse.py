"""LLamaParse module for document parsing using LlamaIndex.

This module provides functionality for parsing and processing documents using
LlamaIndex capabilities. It supports multiple parsing strategies and tools
while maintaining a consistent interface.
"""

from typing import Dict, Any, Optional
import os
import json
import sys
from pathlib import Path
from pydantic import BaseModel, Field
from integrations.aparavi.client import AparaviClient

class LlamaParseClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key


class LlamaParseResponse(BaseModel):
    """Response from LlamaParse processing."""
    text: str = Field(..., description="Extracted text from the document")
    prompt: Optional[str] = Field(None, description="Optional prompt for further processing")
    status: str = Field(..., description="Processing status")
    

class LLamaParse:
    """LLamaParse class for document parsing and processing.
    
    This class provides two main tools for document parsing:
    1. OCR - System Diagram Parser
    2. LLamaParse - Document Parser
    
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
    
    def ocr_system_diagram_parser(self, file_path: str) -> LlamaParseResponse:
        """Parse system diagrams using OCR capabilities.
        
        Args:
            file_path (str): Path to the system diagram file
            
        Returns:
            LlamaParseResponse: Parsed diagram information
        """
        # Load pipeline configuration from package resources
        package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pipeline_config_path = os.path.join(package_root, "resources", "pipelines", "system_architecture.json")
        
        if not os.path.exists(pipeline_config_path):
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
        file_path = Path(file_path)
        if not file_path.exists():
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
            file_glob=str(file_path.absolute())
        )

        # Extract text from the result
        if responses and responses[0].get('status') == 'OK':
            result = responses[0]
            print(f"\nFull response: {json.dumps(result, indent=2)}", file=sys.stderr)
            
            # For now, return the raw response data
            # TODO: Once we confirm the exact response format, update this to extract specific fields
            return LlamaParseResponse(
                text=json.dumps(result.get('data', {})),
                status="completed",
                prompt="""
                You are a senior systems architect. Given the following components and system layout, write a **clear and professional architecture description** to help an AI developer understand the design.

                Structure your response in **three main layers**:

                1. **UI Layer** – User interfaces, clients, and external-facing systems
                2. **Business Logic Layer** – Application logic, services, authentication, and messaging
                3. **Data Layer** – Databases, file storage, and legacy systems

                Also include a section called:

                **Component Interactions** – Describe the data flow or request flow between components (e.g. “Browser sends request → Web Server → App Server → DB”).
                
                """,
                raw_response=result
            )
        
        return LlamaParseResponse(
            text="",
            status="failed",
            prompt=None
        )

    def llama_parse_document_parser(self, file_path: str) -> Dict[str, Any]:
        """Parse documents using LlamaIndex capabilities.
        
        Args:
            file_path (str): Path to the document to parse
            
        Returns:
            Dict[str, Any]: Parsed document information
        """

        # Load pipeline configuration from package resources
        package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pipeline_config_path = os.path.join(package_root, "resources", "pipelines", "llamaparse.json")
        
        if not os.path.exists(pipeline_config_path):
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
        file_path = Path(file_path)
        if not file_path.exists():
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
            file_glob=str(file_path.absolute())
        )

        # Extract text from the result
        if responses and responses[0].get('status') == 'OK':
            result = responses[0]
            print(f"\nFull response: {json.dumps(result, indent=2)}", file=sys.stderr)
            
            # For now, return the raw response data
            # TODO: Once we confirm the exact response format, update this to extract specific fields
            return LlamaParseResponse(
                text=json.dumps(result.get('data', {})),
                status="completed",
            )
        
        return LlamaParseResponse(
            text="",
            status="failed",
            prompt=None
        )

