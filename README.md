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

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
  - [For Users](#for-users)
  - [For Developers](#for-developers)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Running as a User](#running-as-a-user)
  - [Running for Development](#running-for-development)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- Git (for development setup)

## Quick Start Installation

### For Users

The fastest way to get started is using `npx`:

First get your API-Key [here](https://dtc-dev.aparavi.com)
(you can watch this [video](https://aparavi.com/documentation-aparavi/data-toolchain-for-ai-documentation/getting-started-data-toolchain-for-ai-documentation/overview-8/) for orientation).
 
1. **Run the Server**
   ```bash
   # For Unix/Linux/macOS - Set API keys in terminal
   export APARAVI_API_KEY=your_api_key_here

   # For Windows - Set API keys in Command Prompt
   set APARAVI_API_KEY=your_api_key_here

   # OR for Windows PowerShell
   $env:APARAVI_API_KEY="your_api_key_here"

   # Run the server (same command for all platforms)
   npx aparavi-mcp@latest
   ```

2. **Add Server to your Client**
   Update your `MCP_config.json` file in the client ([Windsurf](https://windsurf.com/university/tutorials/configuring-first-mcp-server), [Claude](https://www.youtube.com/watch?v=DfWHX7kszQI), [Cursor](https://www.youtube.com/watch?v=RCFe1L9qm3E) with this:
   ```json
    {
      "mcpServers": {
        "aparavi": {
          "serverUrl": "http://localhost:8000/mcp"
        }
      }
    }
 
   ```


### For Developers

For local development and testing:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/AparaviSoftware/mcp-server
   cd mcp-server
   ```

2. **Set Up Python Environment**
   ```bash
    npx aparavi-mcp@latest
   ```

3. **Running Tests**
   First, ensure your server is running (from step 1). Then you can run and configure tests:

   ```bash
   # Run the test tool
   python tests/test_tool.py
   ```

   To test different tools or files, open `tests/test_tool.py` and modify the `main()` function:
   ```python
   def main():
       # Change the file path to test different documents
       file_path = "tests/testdata/test_document.txt"
       # Or try other test files:
       # file_path = "tests/testdata/SDD_RoadTrip.pdf"
       # file_path = "tests/testdata/system_diagram.jpeg"

       # Change the tool name to test different tools
       tool_name = "document_processor"
       # Available tools:
       # - "Aparavi_Document_Processor" (for text documents)
       # - "Advanced_OCR_Parser" (for diagrams/images)

       run_tool_test(file_path, tool_name)
   ```

## Configuration

### Required Environment Variables

- `APARAVI_API_KEY`: Your Aparavi API key (required)

## Project Structure

```
aparavi-mcp/
├── bin/                    # Executable scripts
│   ├── index.js           # Node.js entry point
│   └── setup.sh           # Python environment setup
|__ prompts/               #Preconfigured prompts
├── tools/                 # MCP tool implementations
├── resources/             # Configuration and resources
├── tests/                 # Test files
├── mcp-server.py         # Main Python server
├── requirements.txt      # Python dependencies
└── package.json         # Node.js package config
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

