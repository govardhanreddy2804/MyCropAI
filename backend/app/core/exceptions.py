class AppException(Exception):
    """Base exception for application errors."""


class UserAlreadyExistsError(AppException):
    """Raised when a user already exists."""

class InvalidCredentialsError(AppException):
    """Raised when login credentials are invalid."""