"""Test script for the Aparavi MCP server document processing endpoint."""

import asyncio
import aiohttp
import json
import uuid
from pathlib import Path

async def test_document_processing(file_path: str, tool_name: str):
    """Test the document processing endpoint."""
    url = "http://localhost:8000/mcp"
    test_file_path = f"tests/testdata/{file_path}"

    if not Path(test_file_path).exists():
        print(f"Please create a test document at {test_file_path}")
        return

    # Generate a session ID
    session_id = str(uuid.uuid4())

    # JSON-RPC 2.0 format with FastMCP tool call
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": {
                "file_path": str(Path(test_file_path).absolute()),
            }
        },
        "id": "1"
    }

    print("\nStarting document processing test:")
    print(f"- File: {test_file_path}")
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
                            if 'result' in data:
                                print("Raw result:", json.dumps(data['result'], indent=2))

                            elif 'error' in data:
                                print("\nError:", data['error'])
                else:
                    print(f"\nError: HTTP {response.status}")
                    print(await response.text())
        except aiohttp.ClientError as e:
            print(f"\nRequest failed: {e}")


if __name__ == "__main__":
    # Pass the file path and tool name as arguments

    # available tools:
    # Advanced_OCR_Parser
    # Aparavi_Document_Processor

    # available files are all in the tests/testdata folder

    asyncio.run(test_document_processing(file_path="30-60-90-R&D-SFAIINTERNSHIP-DylanSavage.pdf", tool_name="Advanced_OCR_Parser"))
