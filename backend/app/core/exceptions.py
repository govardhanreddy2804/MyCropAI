class AppException(Exception):
    """Base exception for application errors."""


class UserAlreadyExistsError(AppException):
    """Raised when a user already exists."""

class InvalidCredentialsError(AppException):
    """Raised when login credentials are invalid."""


class InvalidRefreshTokenError(AppException):
    """Raised when a refresh token is invalid."""


class RefreshTokenReuseError(AppException):
    """Raised when a revoked refresh token is reused."""