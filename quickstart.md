# Quick Start

## For testing locally 

1. Install package:
```bash
npm install aparavi-mcp
```
(This will automatically create a .venv and install Python dependencies)

2. Set required keys:
```bash
export APARAVI_API_KEY=your_api_key_here
export LLAMA_INDEX_API_KEY=your_api_key_here
```

3. In mcp-server.py
Comment out:
    mcp.run()

Comment in:
    mcp.run(transport="http")

(For information as to why, look at readme.md -> testing)

4. Run server:
```bash
aparavi-mcp
```

5. Run Tests:
```bash
# Activate the virtual environment first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run Aparavi API test
python tests/test_aparavi_connection.py

# Run tool tests (configure test_tool.py first)
python tests/test_tool.py
```

That's it! Server is running at http://localhost:8000

Need more info? Check README.md
