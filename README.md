# Aparavi MCP Server

An MCP (Model Context Protocol) server that integrates with Aparavi's document processing capabilities. This server allows Language Models to process documents through Aparavi's API and receive cleaned text output.

## Quick Start with NPX

The fastest way to get started is using `npx`:

```bash
# Set your Aparavi API key
export APARAVI_API_KEY=your_api_key_here

# Run the server
npx aparavi-mcp
```

## Configuration in MCP Clients

When using this server with MCP clients like Windsurf, configure it in your client's configuration file:

```json
{
  "mcpServers": {
    "aparavi": {
      "command": "npx",
      "args": [
        "-y",
        "aparavi-mcp@latest"
      ],
      "env": {
        "APARAVI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

The client will automatically set up the environment variable when launching the server.

## Features

- Document processing via Aparavi API
- Clean text extraction without metadata
- MCP-compliant interface
- Environment-based configuration
- Async processing support
- Easy installation via NPX

## Development

- Built using FastMCP and FastAPI
- Direct integration with Aparavi API endpoints
- Async processing with aiohttp
- Environment-based configuration

## Configuration

The server requires one environment variable:
- `APARAVI_API_KEY`: Your Aparavi API key (required)

Optional configuration:
- `APARAVI_API_URL`: Aparavi API base URL (default: https://eaas-dev.aparavi.com)
- `SERVER_HOST`: Host to bind server to (default: 0.0.0.0)
- `SERVER_PORT`: Port to bind server to (default: 8000)
- `REQUEST_TIMEOUT`: API request timeout in seconds (default: 90)
- `MAX_RETRIES`: Maximum number of retries for failed requests (default: 3)

## Deployment

This server can be deployed as a standalone service. It's designed to work with any MCP-compatible client, including LLM agents.

## License

[Add your license information here]
