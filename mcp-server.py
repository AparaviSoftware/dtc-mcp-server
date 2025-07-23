"""
Main FastAPI application entry point.
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastmcp.server import FastMCP, Context, server
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from tools.document_processor import DocumentProcessor, DocumentRequest, DocumentResponse
from integrations.aparavi.client import AparaviClient

# Load environment variables
load_dotenv()

@dataclass()
class AppContext:
    client: AparaviClient

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage Aparavi API client lifecycle."""
    api_key = os.getenv("APARAVI_API_KEY")
    if not api_key:
        raise ValueError("APARAVI_API_KEY environment variable is required")
    
    base_url = os.getenv("APARAVI_API_URL", "https://eaas-dev.aparavi.com")
    timeout = int(os.getenv("APARAVI_TIMEOUT", "30"))
    
    client = AparaviClient(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout
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
def document_processor(request: DocumentRequest, session_id: str, ctx: Context) -> DocumentResponse:
    """Process a document through Aparavi API."""
    client = ctx.request_context.lifespan_context.client
    processor = DocumentProcessor(client)
    return processor.process_document(request)


# Create ASGI app for MCP server
# mcp_app = mcp.http_app()

# Create FastAPI app
# app = FastAPI(
#     title="Aparavi MCP Server",
#     description="MCP server for processing documents through Aparavi API",
#     version="0.1.0",
#     lifespan=mcp_app.lifespan
# )
# # Mount MCP server under /mcp-server path
# app.mount("/mcp-server", mcp_app)

if __name__ == "__main__":
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=3001) 
    mcp.run(transport="http")