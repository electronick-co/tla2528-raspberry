"""Enumerations for TLA2528 ADC configuration."""

from enum import IntEnum


class OversamplingRatio(IntEnum):
    """Oversampling ratios for improved precision.

    See datasheet Table 15 (p. 34)
    """
    NONE = 0    # No oversampling
    OSR_2 = 1   # 2x oversampling
    OSR_4 = 2   # 4x oversampling
    OSR_8 = 3   # 8x oversampling
    OSR_16 = 4  # 16x oversampling
    OSR_32 = 5  # 32x oversampling
    OSR_64 = 6  # 64x oversampling
    OSR_128 = 7 # 128x oversampling


class Channel(IntEnum):
    """ADC channel numbers (0-7).

    Each channel can be configured as analog input, digital input, or digital output.
    See datasheet Table 1 (p. 4)
    """
    CH0 = 0
    CH1 = 1
    CH2 = 2
    CH3 = 3
    CH4 = 4
    CH5 = 5
    CH6 = 6
    CH7 = 7


class Mode(IntEnum):
    """Analog input conversion modes.

    MANUAL: Host directly controls when data is sampled via I2C commands.
            The 9th falling edge of SCL (ACK) triggers conversion.
            MUX is controlled by MANUAL_CHID field in CHANNEL_SEL register.

    AUTO_SEQ: Device automatically scans through enabled channels.
              Host must provide continuous SCL clocks.
              MUX auto-increments after each conversion.
    """
    MANUAL = 0
    AUTO_SEQ = 1


class OutputMode(IntEnum):
    """Digital output pin driver mode."""
    OPEN_DRAIN = 0  # Open drain output
    PUSH_PULL = 1   # Push-pull output


class DataFormat(IntEnum):
    """ADC data format for readings."""
    RAW = 0       # 12-bit raw ADC data
    AVERAGED = 1  # 16-bit averaged data (when oversampling enabled)


class Append(IntEnum):
    """Additional data to append to ADC readings."""
    NONE = 0       # No additional data
    CHANNEL_ID = 1 # Append 4-bit channel ID to output


class AlertLogic(IntEnum):
    """Alert pin behavior."""
    ACTIVE_LOW = 0   # ALERT pin active low
    ACTIVE_HIGH = 1  # ALERT pin active high
    PULSED_LOW = 2   # ALERT pin pulsed low per alert
    PULSED_HIGH = 3  # ALERT pin pulsed high per alert


class SequenceMode(IntEnum):
    """Internal sequence mode for analog input scanning."""
    MANUAL = 0  # Manual mode
    AUTO = 1    # Automatic mode
