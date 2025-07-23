from setuptools import setup, find_packages

setup(
    name="mcp-server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "fastmcp",
    ],
    python_requires=">=3.8",
) 