"""Custom exceptions for TLA2528 library."""


class TLA2528Error(Exception):
    """Base exception for all TLA2528 errors."""
    pass


class I2CError(TLA2528Error):
    """I2C communication error."""
    pass


class ConfigurationError(TLA2528Error):
    """Invalid configuration or setup error."""
    pass


class TimeoutError(TLA2528Error):
    """Operation timed out."""
    pass


class CalibrationError(TLA2528Error):
    """Calibration failed."""
    pass


class InvalidChannelError(TLA2528Error):
    """Channel not configured for requested operation."""
    pass
