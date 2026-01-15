"""Register addresses, opcodes, and bit masks for TLA2528 ADC."""

from enum import IntEnum


class Register(IntEnum):
    """Register addresses for TLA2528.

    See datasheet Table 10 (p. 29)
    """
    SYSTEM_STATUS = 0x00
    GENERAL_CFG = 0x01
    DATA_CFG = 0x02
    OSR_CFG = 0x03
    OPMODE_CFG = 0x04
    PIN_CFG = 0x05
    GPIO_CFG = 0x07
    GPO_DRIVE_CFG = 0x09
    GPO_VALUE = 0x0B
    GPI_VALUE = 0x0D
    SEQUENCE_CFG = 0x10
    CHANNEL_SEL = 0x11
    AUTO_SEQ_CH_SEL = 0x12


class Opcode:
    """I2C opcodes for TLA2528 operations.

    See datasheet Table 9 (p. 26)
    """
    GENERAL = 0b00000000      # General call (reset, address programming)
    READ_ONE = 0b00010000     # Read single register
    WRITE_ONE = 0b00001000    # Write single register
    SET_BITS = 0b00011000     # Set specific bits in register
    CLR_BITS = 0b00100000     # Clear specific bits in register
    READ_BLOCK = 0b00110000   # Read multiple registers
    WRITE_BLOCK = 0b00101000  # Write multiple registers


class SystemStatusBits:
    """Bit masks for SYSTEM_STATUS register.

    See datasheet Table 12 (p. 32)
    """
    SEQ_STATUS = (1 << 6)    # Sequence status (0=idle, 1=busy)
    I2C_SPEED = (1 << 5)     # I2C speed (0=100kHz, 1=400kHz)
    OSR_DONE = (1 << 3)      # OSR complete (0=not done, 1=done), clear by writing 1
    CRC_ERR_FUSE = (1 << 2)  # CRC error on power-up config check
    BOR = (1 << 0)           # Brown-out reset detected


class GeneralCfgBits:
    """Bit masks for GENERAL_CFG register.

    See datasheet Table 13 (p. 33)
    """
    CNVST = (1 << 3)   # Control start conversion
    CH_RST = (1 << 2)  # Channel reset (force all to analog inputs)
    CAL = (1 << 1)     # Calibration (1=start calibration)
    SW_RST = (1 << 0)  # Software reset (1=reset all registers)


class DataCfgBits:
    """Bit masks for DATA_CFG register.

    See datasheet Table 14 (p. 33)
    """
    FIX_PAT = (1 << 7)       # Fixed pattern enable
    APPEND = (1 << 4)        # Append channel ID/status
    APPEND_NONE = 0          # No append
    APPEND_CHID = (1 << 4)   # Append 4-bit channel ID


class OsrCfgBits:
    """Bit masks for OSR_CFG register.

    See datasheet Table 15 (p. 34)
    """
    OSR = (1 << 2) | (1 << 1) | (1 << 0)  # Oversampling ratio bits [2:0]


class OpmodeCfgBits:
    """Bit masks for OPMODE_CFG register.

    See datasheet Table 16 (p. 34)
    """
    OSC_SEL = (1 << 4)  # Oscillator selection (0=high-speed, 1=low-power)
    CLK_DIV = (1 << 3) | (1 << 2) | (1 << 1) | (1 << 0)  # Clock divider bits


class SequenceCfgBits:
    """Bit masks for SEQUENCE_CFG register.

    See datasheet Table 22 (p. 36)
    """
    SEQ_START = (1 << 4)  # Start sequence (1=start in ascending channel order)
    SEQ_MODE = (1 << 0)   # Sequence mode (0=manual, 1=autonomous)


class ChannelSelBits:
    """Bit masks for CHANNEL_SEL register.

    See datasheet Table 23 (p. 37)
    """
    CH_SEL = (1 << 3) | (1 << 2) | (1 << 1) | (1 << 0)  # Channel select bits [3:0]
