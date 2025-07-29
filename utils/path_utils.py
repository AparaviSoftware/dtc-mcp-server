"""Cross-platform path handling utilities for MCP server.

This module provides a consistent interface for path operations across different
operating systems (Windows, macOS, Linux). It uses pathlib.Path for all path
manipulations to ensure proper cross-platform compatibility.
"""

from pathlib import Path
import sys
from typing import Union, List, Optional

PathLike = Union[str, Path]

class PathUtils:
    @staticmethod
    def get_package_root() -> Path:
        """Get the absolute path to the package root directory.
        
        Returns:
            Path: Absolute path to the package root directory
        """
        return Path(__file__).parent.parent.resolve()
    
    @staticmethod
    def normalize_path(path: PathLike) -> Path:
        """Convert any path-like object to a normalized Path object.
        
        Args:
            path: Path-like object (string or Path)
            
        Returns:
            Path: Normalized Path object
        """
        return Path(path).resolve()
    
    @staticmethod
    def get_resource_path(resource_path: PathLike) -> Path:
        """Get absolute path to a resource file or directory relative to package root.
        
        Args:
            resource_path: Path to resource relative to package root
            
        Returns:
            Path: Absolute path to the resource
        """
        return PathUtils.get_package_root() / PathUtils.normalize_path(resource_path)
    
    @staticmethod
    def get_venv_python() -> Path:
        """Get path to Python executable in virtual environment.
        
        Returns:
            Path: Path to Python executable in venv
        """
        venv_path = PathUtils.get_package_root() / '.venv'
        if sys.platform == 'win32':
            python_path = venv_path / 'Scripts' / 'python.exe'
        else:
            python_path = venv_path / 'bin' / 'python'
        return python_path
    
    @staticmethod
    def ensure_directory(path: PathLike) -> Path:
        """Ensure a directory exists, creating it if necessary.
        
        Args:
            path: Path to directory
            
        Returns:
            Path: Path to the ensured directory
        """
        path = PathUtils.normalize_path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def is_file_exists(path: PathLike) -> bool:
        """Check if a file exists.
        
        Args:
            path: Path to file
            
        Returns:
            bool: True if file exists, False otherwise
        """
        return PathUtils.normalize_path(path).is_file()
    
    @staticmethod
    def is_directory_exists(path: PathLike) -> bool:
        """Check if a directory exists.
        
        Args:
            path: Path to directory
            
        Returns:
            bool: True if directory exists, False otherwise
        """
        return PathUtils.normalize_path(path).is_dir()
    
    @staticmethod
    def get_relative_path(path: PathLike, relative_to: Optional[PathLike] = None) -> Path:
        """Get path relative to another path or package root.
        
        Args:
            path: Path to make relative
            relative_to: Path to make relative to (defaults to package root)
            
        Returns:
            Path: Relative path
        """
        path = PathUtils.normalize_path(path)
        if relative_to is None:
            relative_to = PathUtils.get_package_root()
        else:
            relative_to = PathUtils.normalize_path(relative_to)
        return path.relative_to(relative_to)
    
    @staticmethod
    def glob_files(pattern: str, root: Optional[PathLike] = None) -> List[Path]:
        """Find files matching a glob pattern.
        
        Args:
            pattern: Glob pattern to match
            root: Root directory to start search from (defaults to package root)
            
        Returns:
            List[Path]: List of matching file paths
        """
        # If pattern is an absolute path, check if it exists directly
        pattern_path = Path(pattern)
        if pattern_path.is_absolute():
            return [pattern_path] if pattern_path.is_file() else []

        # Otherwise, handle as a glob pattern
        if root is None:
            root = PathUtils.get_package_root()
        else:
            root = PathUtils.normalize_path(root)
            
        try:
            return [p for p in root.glob(pattern) if p.is_file()]
        except ValueError:
            # If glob fails, try treating the pattern as a direct relative path
            direct_path = root / pattern
            return [direct_path] if direct_path.is_file() else [] 