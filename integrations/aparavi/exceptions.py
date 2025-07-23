"""Aparavi API exceptions."""

class AparaviError(Exception):
    """Base exception for Aparavi integration"""
    pass


class AuthenticationError(AparaviError):
    """Raised when authentication fails"""
    pass


class ValidationError(AparaviError):
    """Raised when validation fails"""
    pass


class TaskNotFoundError(AparaviError):
    """Raised when a task is not found"""
    pass


class PipelineError(AparaviError):
    """Raised when there is an error with the pipeline configuration."""
    pass

class TaskTimeoutError(AparaviError):
    """Raised when a task fails to become ready within the specified timeout."""
    pass 