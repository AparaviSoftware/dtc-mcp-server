# Aparavi MCP Server

An MCP (Model Context Protocol) server that integrates with Aparavi's document processing capabilities. This server allows Language Models to process documents through Aparavi's API and receive cleaned text output.

[![npm version](https://badge.fury.io/js/aparavi-mcp.svg)](https://www.npmjs.com/package/aparavi-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 📄 Document processing via Aparavi API
- 🧹 Clean text extraction without metadata
- 🔌 MCP-compliant interface
- ⚙️ Environment-based configuration
- 🚀 Async processing support
- 📦 Easy installation via NPX
- 🔍 OCR capabilities for system diagrams
- 🐍 Python-based with Node.js wrapper

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Development Setup](#development-setup)
- [API Documentation](#api-documentation)
- [Testing](#testing)

## Quick Start

The fastest way to get started is using `npx`:

```bash
# Set your Aparavi API key
export APARAVI_API_KEY=your_api_key_here

# Run the server
npx aparavi-mcp
```

## Installation

### NPM Global Installation

```bash
# Install globally
npm install -g aparavi-mcp

# Run the server
aparavi-mcp
```

### Local Development Installation

```bash
# Clone the repository
git clone https://github.com/AparaviSoftware/mcp-server
cd mcp-server

# Make setup script executable
chmod +x bin/setup.sh

# Run setup script (creates virtual environment and installs dependencies)
./bin/setup.sh

# Start the server
node bin/index.js
```

## Configuration

### Required Environment Variables

- `APARAVI_API_KEY`: Your Aparavi API key (required)
- `LLAMA_INDEX_API_KEY`= Your LLama Index API key


### MCP Client Configuration

When using this server with MCP clients like Windsurf, configure it in your client's configuration file:

```json
{
  "mcpServers": {
    "aparavi": {
      "command": "npx",
      "args": [
        "aparavi-mcp@latest"
      ],
      "env": {
        "APARAVI_API_KEY": "your-api-key-here"
        "LLAMA_INDEX_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn

### Virtual Environment

This project uses Python's virtual environment for dependency management. The virtual environment is stored in the `.venv` directory.

For local development:
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

When installing via npm, the virtual environment is automatically managed by the setup script.

### Project Structure

```
aparavi-mcp/
├── bin/                    # Executable scripts
│   ├── index.js           # Node.js entry point
│   └── setup.sh           # Python environment setup
├── integrations/          # External service integrations
├── tools/                 # MCP tool implementations
├── resources/             # Configuration and resources
├── tests/                 # Test files
├── mcp-server.py         # Main Python server
├── requirements.txt      # Python dependencies
└── package.json         # Node.js package config
```

## API Documentation

### Document Processing

Process documents through the Aparavi pipeline:

```python
# Example Python client code
import requests

response = requests.post("http://localhost:8000/mcp", json={
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "document_processor",
        "arguments": {
            "file_path": "/path/to/document.pdf",
            "session_id": "unique-session-id"
        }
    },
    "id": "1"
})
```

### System Diagram OCR

Process system diagrams with OCR capabilities:

```python
response = requests.post("http://localhost:8000/mcp", json={
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "llama_parse_document_parser",
        "arguments": {
            "file_path": "/path/to/diagram.jpeg"
        }
    },
    "id": "1"
})
```

## Testing

### Testing Locally

IMPORTANT:
- When testing locally I have found it easier to use transport="http", so when you want to run tests in your terminal then make sure you are running the server with:
mcp.run(transport="http")
  This is commented out inside of main() in mcp-server.py
- The MCPserver runs with transport="stdio" when running in clients. If you are making changes locally and expect to see them in your client that is running your MCP server, you need to use mcp.run() in mcp-server.py and your MCP_config.json should look like this: 
  {
    "mcpServers": {
      "aparavi": {
        "command": "node",
        "args": [
          "/Your/Path/To/mcp-server/bin/index.js"
        ],
        "env": {
          "APARAVI_API_KEY": "",
          "LLAMA_INDEX_API_KEY": ""
        }
      }
    }
  }

```bash
# Activate virtual environment if not already active
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run Aparavi API test
python tests/test_aparavi_connection.py

# To run tests with specific tools, open tests/test_tool.py and configure main() to which test document and tool you want to test. Then run:
python tests/test_tool.py 
```


