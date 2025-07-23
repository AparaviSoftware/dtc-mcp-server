"""Test script for the Aparavi MCP server document processing endpoint."""

import asyncio
import aiohttp
import json
import uuid
from pathlib import Path
from tools.document_processor import DocumentRequest

async def test_document_processing(processing_type: str = "cpu"):
    """
    Test the document processing endpoint.
    
    Args:
        processing_type: Type of processing to use ('gpu' or 'cpu')
    """
    url = "http://localhost:8000/mcp"  # Updated to match server mount point
    test_file_path = "tests/testdata/test_document.txt"
    
    if not Path(test_file_path).exists():
        print(f"Please create a test document at {test_file_path}")
        return
    
    # Create DocumentRequest instance
    request = DocumentRequest(
        file_path=str(Path(test_file_path).absolute()),
        type=processing_type
    )
    
    # Generate a session ID
    session_id = str(uuid.uuid4())
    
    # JSON-RPC 2.0 format with FastMCP tool call
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "document_processor",
            "arguments": {
                "request": request.model_dump(),
                "session_id": session_id
            }
        },
        "id": "1"
    }
    
    print(f"\nStarting document processing test:")
    print(f"- File: {test_file_path}")
    print(f"- Processing type: {processing_type}")
    print(f"- Session ID: {session_id}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers={
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json",
                "x-mcp-session-id": session_id
            }) as response:
                if response.status == 200:
                    print("\nProcessing started successfully")
                    # Handle server-sent events
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data = json.loads(line[6:])  # Skip 'data: ' prefix
                            print("\nRaw output from document processor:")
                            print(json.dumps(data, indent=2))
                else:
                    print(f"\nError: HTTP {response.status}")
                    print(await response.text())
        except aiohttp.ClientError as e:
            print(f"\nRequest failed: {e}")

async def run_tests():
    """Run tests with both GPU and CPU processing."""
    print("Testing GPU processing...")
    await test_document_processing("cpu")

if __name__ == "__main__":
    asyncio.run(run_tests()) 