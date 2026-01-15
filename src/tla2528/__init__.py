"""TLA2528 ADC Python Library for Raspberry Pi and Linux.

This library provides a Python interface to the TLA2528 family of ADC chips
over I2C on Linux systems, particularly Raspberry Pi.

Example:
    >>> from tla2528 import TLA2528, Channel, OversamplingRatio
    >>> adc = TLA2528(
    ...     bus=1,
    ...     address=0x10,
    ...     analog_inputs=[Channel.CH0, Channel.CH1, Channel.CH2],
    ...     oversampling_ratio=OversamplingRatio.OSR_16
    ... )
    >>> voltage = adc.get_mv(Channel.CH0)
    >>> print(f"Channel 0: {voltage:.2f} mV")
"""

from .enums import (
    AlertLogic,
    Append,
    Channel,
    DataFormat,
    Mode,
    OutputMode,
    OversamplingRatio,
    SequenceMode,
)
from .exceptions import (
    CalibrationError,
    ConfigurationError,
    I2CError,
    InvalidChannelError,
    TLA2528Error,
    TimeoutError,
)
from .tla2528 import TLA2528

__version__ = "0.1.0"

__all__ = [
    # Main class
    "TLA2528",
    # Enums
    "AlertLogic",
    "Append",
    "Channel",
    "DataFormat",
    "Mode",
    "OutputMode",
    "OversamplingRatio",
    "SequenceMode",
    # Exceptions
    "CalibrationError",
    "ConfigurationError",
    "I2CError",
    "InvalidChannelError",
    "TLA2528Error",
    "TimeoutError",
]
