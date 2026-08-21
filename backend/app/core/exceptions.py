class AppException(Exception):
    """Base exception for application errors."""


class UserAlreadyExistsError(AppException):
    """Raised when a user already exists."""