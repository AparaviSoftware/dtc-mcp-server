"""Aparavi MCP Server

A Model Context Protocol (MCP) server that integrates with Aparavi's document processing capabilities.
This server allows Language Models to process documents through Aparavi's pipeline and receive cleaned text output.
"""

from . import tools
from . import prompts
from . import resources
from . import config

__version__ = "0.1.0"
__all__ = ["tools", "prompts", "resources", "config"] 