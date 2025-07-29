"""Test MIME type handling for different file types."""

import mimetypes
from pathlib import Path

def test_mime_types():
    """Print MIME types for different file extensions."""
    test_files = [
        "test.pdf",
        "test.txt",
        "test.jpeg",
        "test.jpg",
        "test.png"
    ]
    
    print("\nMIME Type Detection:")
    print("-" * 40)
    for file in test_files:
        mime_type = mimetypes.guess_type(file)[0] or "application/octet-stream"
        print(f"{file:15} -> {mime_type}") 

if __name__ == "__main__":
    test_mime_types()