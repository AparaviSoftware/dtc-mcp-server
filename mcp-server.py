"""
Main FastAPI application entry point.
"""
import os
from dotenv import load_dotenv
from fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator
from tools.document_processor import DocumentProcessor, DocumentResponse
from tools.llama_parse import LLamaParse, LlamaParseResponse
from aparavi_dtc_sdk import AparaviClient

# Load environment variables
load_dotenv()

@dataclass()
class AppContext:
    client: AparaviClient

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage Aparavi API client and LlamaParse client lifecycle."""
    # Aparavi client setup
    aparavi_api_key = os.getenv("APARAVI_API_KEY")
    if not aparavi_api_key:
        raise ValueError("APARAVI_API_KEY environment variable is required")

    base_url = os.getenv("APARAVI_API_URL", "https://eaas-dev.aparavi.com")

    client = AparaviClient(
        base_url=base_url,
        api_key=aparavi_api_key,
    )

    try:
        yield AppContext(client=client)
    finally:
        pass

# Create FastMCP instance with dependencies
mcp = FastMCP(
    name="aparavi-mcp",
    lifespan=app_lifespan,
    dependencies=["python-dotenv"],
    stateless_http=True
)

# Register document processing tool
@mcp.tool()
def Aparavi_Document_Processor(file_path: str, session_id: str = None, ctx: Context = None) -> DocumentResponse:
    """
    Use Aparavi to process a document.
    """
    client = ctx.request_context.lifespan_context.client
    processor = DocumentProcessor(client)
    return processor.SDK_Document_Processor(file_path=file_path)

@mcp.tool()
def Advanced_OCR_Parser(file_path: str, session_id: str = None, ctx: Context = None) -> LlamaParseResponse:
    """
    Use LlamaParse's advanced Parsing capabilities to extract text from a document.
    """
    aparavi_client = ctx.request_context.lifespan_context.client

    parser = LLamaParse(aparavi_client)
    return parser.SDK_LlamaParse(file_path=file_path)

if __name__ == "__main__":

    mcp.run(transport="http")

