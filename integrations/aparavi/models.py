"""
Data models for Aparavi integration
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ResultBase:
    """Base class for API responses with a standardized format."""
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None


@dataclass
class Result:
    """A generic result with no data."""
    status: str
    data: Optional[None] = None
    error: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None


@dataclass
class ValidationError:
    """Validation error details."""
    loc: list
    msg: str
    type: str


@dataclass
class HTTPValidationError:
    """HTTP validation error containing multiple validation errors."""
    detail: list[ValidationError] 