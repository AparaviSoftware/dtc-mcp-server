"""Tests for cross-platform path handling utilities."""

import os
import sys
import tempfile
from pathlib import Path
from utils.path_utils import PathUtils

def test_get_package_root():
    """Test package root resolution."""
    root = PathUtils.get_package_root()
    assert root.is_dir()
    assert (root / 'utils' / 'path_utils.py').is_file()

def test_normalize_path():
    """Test path normalization."""
    # Test with string path
    path_str = "utils/path_utils.py"
    norm_path = PathUtils.normalize_path(path_str)
    assert isinstance(norm_path, Path)
    assert norm_path.is_absolute()
    
    # Test with Path object
    path_obj = Path("utils") / "path_utils.py"
    norm_path = PathUtils.normalize_path(path_obj)
    assert isinstance(norm_path, Path)
    assert norm_path.is_absolute()

def test_get_resource_path():
    """Test resource path resolution."""
    resource_path = PathUtils.get_resource_path("resources/pipelines/simpleparser.json")
    assert resource_path.is_absolute()
    assert resource_path.exists()
    assert resource_path.is_file()

def test_get_venv_python():
    """Test virtual environment Python path."""
    python_path = PathUtils.get_venv_python()
    assert python_path.is_absolute()
    
    # Check platform-specific path
    if sys.platform == 'win32':
        assert python_path.name == 'python.exe'
        assert 'Scripts' in python_path.parts
    else:
        assert python_path.name == 'python'
        assert 'bin' in python_path.parts

def test_ensure_directory():
    """Test directory creation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "test_dir" / "nested"
        created_dir = PathUtils.ensure_directory(test_dir)
        assert created_dir.exists()
        assert created_dir.is_dir()
        assert str(created_dir) == str(test_dir.resolve())

def test_file_exists():
    """Test file existence check."""
    assert PathUtils.is_file_exists("utils/path_utils.py")
    assert not PathUtils.is_file_exists("nonexistent_file.txt")

def test_directory_exists():
    """Test directory existence check."""
    assert PathUtils.is_directory_exists("utils")
    assert not PathUtils.is_directory_exists("nonexistent_dir")

def test_get_relative_path():
    """Test relative path calculation."""
    abs_path = PathUtils.get_package_root() / "utils" / "path_utils.py"
    rel_path = PathUtils.get_relative_path(abs_path)
    assert str(rel_path) == os.path.join("utils", "path_utils.py")
    
    # Test with custom base
    base = PathUtils.get_package_root() / "utils"
    rel_path = PathUtils.get_relative_path(abs_path, base)
    assert str(rel_path) == "path_utils.py"

def test_glob_files():
    """Test glob pattern matching."""
    # Test JSON files in pipelines
    json_files = PathUtils.glob_files("*.json", "resources/pipelines")
    assert len(json_files) >= 2  # simpleparser.json and llamaparse.json
    assert all(f.suffix == '.json' for f in json_files)
    
    # Test Python files in tools
    py_files = PathUtils.glob_files("*.py", "utils")
    assert "path_utils.py" in [f.name for f in py_files] 

def run_all_tests():
    """Run all test functions and report results."""
    test_functions = [
        test_get_package_root,
        test_normalize_path,
        test_get_resource_path,
        test_get_venv_python,
        test_ensure_directory,
        test_file_exists,
        test_directory_exists,
        test_get_relative_path,
        test_glob_files
    ]
    
    passed = 0
    failed = 0
    
    print("\nRunning path utilities tests...")
    print("-" * 40)
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
            print(f"✓ {test_func.__name__}")
        except Exception as e:
            failed += 1
            print(f"✗ {test_func.__name__}")
            print(f"  Error: {str(e)}")
    
    print("-" * 40)
    print(f"Results: {passed} passed, {failed} failed")
    print(f"Total: {passed + failed} tests")
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1) 