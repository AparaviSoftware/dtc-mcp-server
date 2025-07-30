# MCP Server - Windows Installation Guide

This guide provides step-by-step instructions for setting up and running the MCP (Model Context Protocol) server on Windows.

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **Command Prompt** or **PowerShell** access

## 🚀 Quick Start

### 1. Clone the Repository
```cmd
git clone https://github.com/AparaviSoftware/mcp-server.git
cd mcp-server
```

### 2. Create Virtual Environment
```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies (Two-Step Process)

Due to package conflicts between main PyPI and test PyPI, we use a two-step installation:

**Step 1: Install core packages**
```cmd
pip install -r requirements.txt
```

**Step 2: Install special packages from test PyPI**
```cmd
pip install -r requirements-testpypi.txt
```

### 4. Run npx
# Run the server
open a new terminal
# Set your Aparavi API key
export APARAVI_API_KEY=your_api_key_here

npx aparavi-mcp

### 5 : Test python

use the same env .venv
(.venv) C:\mcp-server>python .\tests\test_tool.py
