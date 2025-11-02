"""
Custom Exceptions
Application-specific exception classes for better error handling
"""

from fastapi import HTTPException, status


class WorthWiseException(Exception):
    """Base exception for WorthWise application"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class DatabaseException(WorthWiseException):
    """Database connection or query error"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, error_code="DATABASE_ERROR")


class DataNotFoundException(WorthWiseException):
    """Requested data not found"""
    def __init__(self, message: str = "Requested data not found"):
        super().__init__(message, error_code="DATA_NOT_FOUND")


class ValidationException(WorthWiseException):
    """Data validation error"""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, error_code="VALIDATION_ERROR")


class ComputationException(WorthWiseException):
    """Error during ROI computation"""
    def __init__(self, message: str = "Computation failed"):
        super().__init__(message, error_code="COMPUTATION_ERROR")


class InsufficientDataException(WorthWiseException):
    """Insufficient data for computation"""
    def __init__(self, message: str = "Insufficient data for calculation"):
        super().__init__(message, error_code="INSUFFICIENT_DATA")


def handle_database_error(e: Exception) -> HTTPException:
    """Convert database errors to HTTP exceptions"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Database error: {str(e)}"
    )


def handle_not_found_error(resource: str) -> HTTPException:
    """Create not found HTTP exception"""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found"
    )


def handle_validation_error(message: str) -> HTTPException:
    """Create validation HTTP exception"""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message
    )

