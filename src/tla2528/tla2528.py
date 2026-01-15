"""TLA2528 ADC driver for Raspberry Pi and Linux."""

import logging
import time
from threading import RLock
from typing import Dict, List, Optional, Union

try:
    from smbus2 import SMBus
except ImportError:
    SMBus = None  # Allow import without smbus2 for testing

from .enums import (
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
    TimeoutError,
)
from .registers import (
    ChannelSelBits,
    DataCfgBits,
    GeneralCfgBits,
    Opcode,
    Register,
    SequenceCfgBits,
    SystemStatusBits,
)


class TLA2528:
    """TLA2528 ADC driver for Linux/Raspberry Pi.

    The TLA2528 is a 12/16-bit, 8-channel ADC with 8 digital I/O pins.
    It supports manual and auto-sequence sampling modes, oversampling
    ratios from 2x to 128x, and configurable analog/digital I/O.

    Datasheet: https://www.ti.com/lit/ds/symlink/tla2528.pdf

    Example:
        >>> from tla2528 import TLA2528, Channel, OversamplingRatio
        >>> adc = TLA2528(
        ...     bus=1,
        ...     address=0x10,
        ...     analog_inputs=[Channel.CH0, Channel.CH1]
        ... )
        >>> voltage = adc.get_mv(Channel.CH0)
        >>> print(f"CH0: {voltage:.2f} mV")
    """

    DEFAULT_ADDRESS = 0x10  # Default I2C address (R1 and R2 DNP)

    def __init__(
        self,
        bus: Union[int, SMBus],
        address: int = DEFAULT_ADDRESS,
        avdd_volts: float = 3.3,
        mode: Mode = Mode.MANUAL,
        analog_inputs: Optional[List[Channel]] = None,
        digital_inputs: Optional[List[Channel]] = None,
        digital_outputs: Optional[List[Channel]] = None,
        digital_output_modes: Optional[Dict[Channel, OutputMode]] = None,
        digital_output_values: Optional[Dict[Channel, bool]] = None,
        oversampling_ratio: OversamplingRatio = OversamplingRatio.NONE,
        append: Append = Append.NONE,
        auto_init: bool = True,
        auto_calibrate: bool = False,
        log_level: int = logging.WARNING,
    ):
        """Initialize TLA2528 ADC.

        Args:
            bus: I2C bus number or SMBus instance
            address: I2C device address (default 0x10)
            avdd_volts: AVDD reference voltage in volts (default 3.3V)
            mode: Sampling mode (MANUAL or AUTO_SEQ)
            analog_inputs: List of channels configured as analog inputs
            digital_inputs: List of channels configured as digital inputs
            digital_outputs: List of channels configured as digital outputs
            digital_output_modes: Output modes for digital output channels
            digital_output_values: Initial values for digital output channels
            oversampling_ratio: Oversampling ratio for improved precision
            append: Additional data to append to readings
            auto_init: Automatically initialize device on construction
            auto_calibrate: Automatically calibrate after initialization
            log_level: Logging level (default: WARNING)

        Raises:
            I2CError: If I2C communication fails
            ConfigurationError: If configuration is invalid
        """
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # I2C setup
        if isinstance(bus, int):
            if SMBus is None:
                raise ImportError(
                    "smbus2 is required. Install with: pip install smbus2"
                )
            self._bus = SMBus(bus)
            self._bus_owned = True
        else:
            self._bus = bus
            self._bus_owned = False

        self._address = address
        self._lock = RLock()

        # Configuration
        self._mode = mode
        self._avdd_mv = avdd_volts * 1000.0
        self._oversampling_ratio = oversampling_ratio
        self._data_format = (
            DataFormat.RAW
            if oversampling_ratio == OversamplingRatio.NONE
            else DataFormat.AVERAGED
        )
        self._append = append
        self._analog_inputs = analog_inputs or []
        self._digital_inputs = digital_inputs or []
        self._digital_outputs = digital_outputs or []
        self._digital_output_modes = digital_output_modes or {}
        self._digital_output_values = digital_output_values or {}

        # Calculate bytes per sample
        self._num_bytes_per_sample = 2
        if (
            self._data_format == DataFormat.AVERAGED
            and self._append == Append.CHANNEL_ID
        ):
            self._num_bytes_per_sample = 3

        # Initialize if requested
        if auto_init:
            self.initialize()
            if auto_calibrate:
                self.calibrate()

    def __del__(self):
        """Clean up resources."""
        if hasattr(self, "_bus_owned") and self._bus_owned and hasattr(self, "_bus"):
            try:
                self._bus.close()
            except Exception:
                pass

    def initialize(self) -> None:
        """Initialize the ADC with the configured settings.

        This configures the ADC pins, mode, oversampling, and other settings
        based on the configuration provided during construction.

        Raises:
            I2CError: If I2C communication fails
            ConfigurationError: If configuration is invalid
        """
        with self._lock:
            self.logger.info("Initializing TLA2528")

            # Set data format
            self._set_data_format(self._data_format, self._append)

            # Set oversampling ratio
            self._set_oversampling_ratio(self._oversampling_ratio)

            # Set pin configuration (analog vs digital)
            self._set_pin_configuration()

            # Set digital output modes
            for channel, output_mode in self._digital_output_modes.items():
                self.set_digital_output_mode(channel, output_mode)

            # Set digital output initial values
            for channel, value in self._digital_output_values.items():
                self.set_digital_output_value(channel, value)

            # Set digital I/O direction
            self._set_digital_io_direction()

            # Set analog inputs
            self._set_analog_inputs()

            # Set operational mode
            self._set_operational_mode()

            self.logger.info("TLA2528 initialized successfully")

    def calibrate(
        self, poll_interval: float = 0.010, timeout: float = 0.100
    ) -> None:
        """Calibrate the ADC.

        Starts the calibration process and waits for it to complete.
        The CAL bit in GENERAL_CFG register is set, then polled until cleared.

        Args:
            poll_interval: Time between calibration status polls (seconds)
            timeout: Maximum time to wait for calibration (seconds)

        Raises:
            TimeoutError: If calibration doesn't complete within timeout
            I2CError: If I2C communication fails
        """
        with self._lock:
            self.logger.info("Starting calibration")
            self._set_bits(Register.GENERAL_CFG, GeneralCfgBits.CAL)

            start_time = time.time()
            while self._read_one(Register.GENERAL_CFG) & GeneralCfgBits.CAL:
                time.sleep(poll_interval)
                if time.time() - start_time > timeout:
                    raise TimeoutError("Calibration timed out")

            self.logger.info("Calibration complete")

    def get_mv(self, channel: Channel) -> float:
        """Read analog voltage from a single channel.

        Args:
            channel: Channel to read

        Returns:
            Voltage in millivolts

        Raises:
            InvalidChannelError: If channel not configured as analog input
            I2CError: If I2C communication fails
        """
        with self._lock:
            # Trigger conversion and read result
            self._trigger_conversion(channel)
            data = self._read_many(self._num_bytes_per_sample)
            raw = self._parse_frame(data)
            return self._raw_to_mv(raw)

    def get_all_mv(self) -> List[float]:
        """Read analog voltages from all configured channels.

        Returns:
            List of voltages in millivolts (in order of analog_inputs)

        Raises:
            ConfigurationError: If not in AUTO_SEQ mode
            I2CError: If I2C communication fails
        """
        with self._lock:
            raw_values = self._read_all()
            return [self._raw_to_mv(raw) for raw in raw_values]

    def get_all_mv_map(self) -> Dict[Channel, float]:
        """Read analog voltages from all configured channels as a dictionary.

        Returns:
            Dictionary mapping Channel to voltage in millivolts

        Raises:
            ConfigurationError: If not in AUTO_SEQ mode
            I2CError: If I2C communication fails
        """
        with self._lock:
            raw_values = self._read_all()
            return {
                channel: self._raw_to_mv(raw)
                for channel, raw in zip(self._analog_inputs, raw_values)
            }

    def set_digital_output_mode(
        self, channel: Channel, output_mode: OutputMode
    ) -> None:
        """Configure digital output mode for a channel.

        Args:
            channel: Channel to configure
            output_mode: Output mode (OPEN_DRAIN or PUSH_PULL)

        Raises:
            InvalidChannelError: If channel not configured as digital output
            I2CError: If I2C communication fails
        """
        with self._lock:
            if not self._is_digital_output(channel):
                raise InvalidChannelError(
                    f"Channel {channel} is not configured as a digital output"
                )

            if output_mode == OutputMode.OPEN_DRAIN:
                self._clear_bits(Register.GPO_DRIVE_CFG, 1 << int(channel))
            else:
                self._set_bits(Register.GPO_DRIVE_CFG, 1 << int(channel))

    def set_digital_output_value(self, channel: Channel, value: bool) -> None:
        """Set digital output value for a channel.

        Args:
            channel: Channel to set
            value: Output value (True=high, False=low)

        Raises:
            InvalidChannelError: If channel not configured as digital output
            I2CError: If I2C communication fails
        """
        with self._lock:
            if not self._is_digital_output(channel):
                raise InvalidChannelError(
                    f"Channel {channel} is not configured as a digital output"
                )

            if value:
                self._set_bits(Register.GPO_VALUE, 1 << int(channel))
            else:
                self._clear_bits(Register.GPO_VALUE, 1 << int(channel))

    def get_digital_input_value(self, channel: Channel) -> bool:
        """Read digital input value from a channel.

        Args:
            channel: Channel to read

        Returns:
            Digital input value (True=high, False=low)

        Raises:
            InvalidChannelError: If channel not configured as digital input
            I2CError: If I2C communication fails
        """
        with self._lock:
            if not self._is_digital_input(channel):
                raise InvalidChannelError(
                    f"Channel {channel} is not configured as a digital input"
                )

            value = self._read_one(Register.GPI_VALUE)
            return bool(value & (1 << int(channel)))

    def get_digital_input_values(self) -> int:
        """Read all digital input values as a bitfield.

        Returns:
            8-bit value where each bit represents a channel (LSB=CH0, MSB=CH7)

        Raises:
            I2CError: If I2C communication fails
        """
        return self._read_one(Register.GPI_VALUE)

    def reset(self) -> None:
        """Perform software reset of the device.

        This resets all registers to default values, converting all channels
        to analog inputs and disabling all events.

        Raises:
            I2CError: If I2C communication fails
        """
        with self._lock:
            self.logger.info("Resetting device")
            self._write_one(Register.GENERAL_CFG, GeneralCfgBits.SW_RST)
            time.sleep(0.010)  # Wait for reset to complete

    # ========================================================================
    # Low-level I2C operations
    # ========================================================================

    def _read_one(self, reg: Register) -> int:
        """Read a single register.

        Args:
            reg: Register to read

        Returns:
            Register value (8-bit)

        Raises:
            I2CError: If I2C communication fails
        """
        with self._lock:
            try:
                # Send read command
                self._bus.write_i2c_block_data(
                    self._address, Opcode.READ_ONE, [int(reg)]
                )
                # Read result
                data = self._bus.read_byte(self._address)
                return data
            except Exception as e:
                raise I2CError(f"Failed to read register {reg}: {e}")

    def _write_one(self, reg: Register, value: int) -> None:
        """Write a single register.

        Args:
            reg: Register to write
            value: Value to write (8-bit)

        Raises:
            I2CError: If I2C communication fails
        """
        with self._lock:
            try:
                self._bus.write_i2c_block_data(
                    self._address, Opcode.WRITE_ONE, [int(reg), value]
                )
            except Exception as e:
                raise I2CError(f"Failed to write register {reg}: {e}")

    def _set_bits(self, reg: Register, bits: int) -> None:
        """Set specific bits in a register.

        Args:
            reg: Register to modify
            bits: Bit mask of bits to set

        Raises:
            I2CError: If I2C communication fails
        """
        with self._lock:
            try:
                self._bus.write_i2c_block_data(
                    self._address, Opcode.SET_BITS, [int(reg), bits]
                )
            except Exception as e:
                raise I2CError(f"Failed to set bits in register {reg}: {e}")

    def _clear_bits(self, reg: Register, bits: int) -> None:
        """Clear specific bits in a register.

        Args:
            reg: Register to modify
            bits: Bit mask of bits to clear

        Raises:
            I2CError: If I2C communication fails
        """
        with self._lock:
            try:
                self._bus.write_i2c_block_data(
                    self._address, Opcode.CLR_BITS, [int(reg), bits]
                )
            except Exception as e:
                raise I2CError(f"Failed to clear bits in register {reg}: {e}")

    def _read_many(self, num_bytes: int) -> bytes:
        """Read multiple bytes from the device.

        Args:
            num_bytes: Number of bytes to read

        Returns:
            Bytes read from device

        Raises:
            I2CError: If I2C communication fails
        """
        with self._lock:
            try:
                data = self._bus.read_i2c_block_data(self._address, 0, num_bytes)
                return bytes(data)
            except Exception as e:
                raise I2CError(f"Failed to read {num_bytes} bytes: {e}")

    # ========================================================================
    # Configuration methods
    # ========================================================================

    def _set_data_format(self, data_format: DataFormat, append: Append) -> None:
        """Configure data format and append mode."""
        self._data_format = data_format
        self._append = append
        self.logger.info(f"Data format: {data_format}, Append: {append}")

        self._clear_bits(Register.DATA_CFG, DataCfgBits.APPEND)
        if append == Append.CHANNEL_ID:
            self._set_bits(Register.DATA_CFG, DataCfgBits.APPEND_CHID)

    def _set_oversampling_ratio(self, ratio: OversamplingRatio) -> None:
        """Configure oversampling ratio."""
        self._write_one(Register.OSR_CFG, int(ratio))

    def _set_pin_configuration(self) -> None:
        """Configure pins as analog or digital."""
        self.logger.info(
            f"Setting digital mode for outputs {self._digital_outputs} "
            f"and inputs {self._digital_inputs}"
        )

        # Build bit mask: 0=analog, 1=digital
        data = 0
        for channel in self._digital_inputs:
            data |= 1 << int(channel)
        for channel in self._digital_outputs:
            data |= 1 << int(channel)

        self._write_one(Register.PIN_CFG, data)

    def _set_digital_io_direction(self) -> None:
        """Configure digital I/O direction."""
        self.logger.info(f"Setting digital outputs: {self._digital_outputs}")

        # Build bit mask: 0=input, 1=output
        data = 0
        for channel in self._digital_outputs:
            data |= 1 << int(channel)

        self._write_one(Register.GPIO_CFG, data)

    def _set_analog_inputs(self) -> None:
        """Configure analog input channels."""
        self.logger.info(f"Setting analog inputs: {self._analog_inputs}")

        if self._mode == Mode.AUTO_SEQ:
            # Configure channels for auto-sequence mode
            data = 0
            for channel in self._analog_inputs:
                data |= 1 << int(channel)
            self._write_one(Register.AUTO_SEQ_CH_SEL, data)

    def _set_operational_mode(self) -> None:
        """Set operational mode (manual or auto-sequence)."""
        if self._mode == Mode.MANUAL:
            self._set_sequence_mode(SequenceMode.MANUAL)
        else:
            self._set_sequence_mode(SequenceMode.AUTO)

    def _set_sequence_mode(self, mode: SequenceMode) -> None:
        """Set sequence mode in SEQUENCE_CFG register."""
        if mode == SequenceMode.AUTO:
            self.logger.info("Setting auto sequence mode")
            self._set_bits(Register.SEQUENCE_CFG, SequenceCfgBits.SEQ_MODE)
        else:
            self.logger.info("Setting manual sequence mode")
            self._clear_bits(Register.SEQUENCE_CFG, SequenceCfgBits.SEQ_MODE)

    # ========================================================================
    # ADC reading methods
    # ========================================================================

    def _read_all(self) -> List[int]:
        """Read all configured analog channels (AUTO_SEQ mode only).

        Returns:
            List of raw ADC values

        Raises:
            ConfigurationError: If not in AUTO_SEQ mode
        """
        if self._mode == Mode.MANUAL:
            raise ConfigurationError("read_all requires AUTO_SEQ mode")

        self.logger.info("Reading all channels")
        num_inputs = len(self._analog_inputs)
        num_bytes = num_inputs * self._num_bytes_per_sample

        # Start auto conversion
        self._start_auto_conversion()

        # Read data
        raw_data = self._read_many(num_bytes)

        # Stop auto conversion
        self._stop_auto_conversion()

        # Parse frames
        values = []
        for i in range(0, num_bytes, self._num_bytes_per_sample):
            frame = raw_data[i : i + self._num_bytes_per_sample]
            values.append(self._parse_frame(frame))

        return values

    def _start_auto_conversion(self) -> None:
        """Start auto-sequence conversion."""
        if self._mode == Mode.MANUAL:
            raise ConfigurationError("Cannot start auto conversion in MANUAL mode")

        self.logger.info("Starting auto conversion")
        self._set_bits(Register.SEQUENCE_CFG, SequenceCfgBits.SEQ_START)

    def _stop_auto_conversion(self) -> None:
        """Stop auto-sequence conversion."""
        if self._mode == Mode.MANUAL:
            raise ConfigurationError("Cannot stop auto conversion in MANUAL mode")

        self.logger.info("Stopping auto conversion")
        self._clear_bits(Register.SEQUENCE_CFG, SequenceCfgBits.SEQ_START)

    def _trigger_conversion(self, channel: Channel) -> None:
        """Trigger conversion for a specific channel (MANUAL mode).

        Args:
            channel: Channel to convert

        Raises:
            InvalidChannelError: If channel not configured as analog input
        """
        if not self._is_analog_input(channel):
            raise InvalidChannelError(
                f"Channel {channel} is not configured as an analog input"
            )

        self.logger.info(f"Triggering conversion for channel {channel}")
        self._select_channel(channel)

    def _select_channel(self, channel: Channel) -> None:
        """Select channel for manual conversion.

        Args:
            channel: Channel to select

        Raises:
            ConfigurationError: If not in MANUAL mode
        """
        if self._mode != Mode.MANUAL:
            raise ConfigurationError("Cannot select channel in non-MANUAL mode")

        self.logger.info(f"Selecting channel {channel}")
        self._write_one(Register.CHANNEL_SEL, int(channel))

    def _parse_frame(self, frame: bytes) -> int:
        """Parse ADC data frame.

        Args:
            frame: Raw frame data

        Returns:
            Parsed ADC value
        """
        msb = frame[0]
        lsb = frame[1]

        if self._data_format == DataFormat.RAW:
            # 12-bit value
            value = (msb << 4) | (lsb >> 4)
        else:
            # 16-bit value
            value = (msb << 8) | lsb

        if self._append == Append.CHANNEL_ID:
            if self._num_bytes_per_sample == 3:
                channel_id = frame[2] >> 4
            else:
                channel_id = lsb & 0x0F
            self.logger.debug(f"Channel ID: {channel_id}, Value: {value}")

        return value

    # ========================================================================
    # Conversion methods
    # ========================================================================

    def _raw_to_mv(self, raw: int) -> float:
        """Convert raw ADC value to millivolts.

        Args:
            raw: Raw ADC value

        Returns:
            Voltage in millivolts
        """
        if self._data_format == DataFormat.AVERAGED:
            # 16-bit ADC
            return float(raw) * self._avdd_mv / 65536.0
        else:
            # 12-bit ADC
            return float(raw) * self._avdd_mv / 4096.0

    # ========================================================================
    # Helper methods
    # ========================================================================

    def _is_digital_input(self, channel: Channel) -> bool:
        """Check if channel is configured as digital input."""
        return channel in self._digital_inputs

    def _is_digital_output(self, channel: Channel) -> bool:
        """Check if channel is configured as digital output."""
        return channel in self._digital_outputs

    def _is_analog_input(self, channel: Channel) -> bool:
        """Check if channel is configured as analog input."""
        return channel in self._analog_inputs
