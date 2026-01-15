"""Basic tests for TLA2528 library."""

import pytest
from unittest.mock import Mock, MagicMock
from tla2528 import (
    TLA2528,
    Channel,
    Mode,
    OversamplingRatio,
    DataFormat,
    ConfigurationError,
    InvalidChannelError,
)


class TestEnums:
    """Test enum definitions."""

    def test_channel_values(self):
        """Test channel enum values."""
        assert Channel.CH0 == 0
        assert Channel.CH7 == 7

    def test_oversampling_ratios(self):
        """Test oversampling ratio values."""
        assert OversamplingRatio.NONE == 0
        assert OversamplingRatio.OSR_128 == 7

    def test_mode_values(self):
        """Test mode enum values."""
        assert Mode.MANUAL == 0
        assert Mode.AUTO_SEQ == 1


class TestTLA2528Initialization:
    """Test TLA2528 initialization."""

    def test_init_with_mock_bus(self):
        """Test initialization with mocked I2C bus."""
        mock_bus = Mock()
        mock_bus.write_i2c_block_data = Mock()
        mock_bus.read_byte = Mock(return_value=0)

        adc = TLA2528(
            bus=mock_bus,
            address=0x10,
            analog_inputs=[Channel.CH0],
            auto_init=False,  # Skip init for this test
        )

        assert adc._address == 0x10
        assert Channel.CH0 in adc._analog_inputs

    def test_data_format_selection(self):
        """Test automatic data format selection based on oversampling."""
        mock_bus = Mock()
        mock_bus.write_i2c_block_data = Mock()
        mock_bus.read_byte = Mock(return_value=0)

        # No oversampling -> RAW format
        adc1 = TLA2528(
            bus=mock_bus,
            oversampling_ratio=OversamplingRatio.NONE,
            auto_init=False,
        )
        assert adc1._data_format == DataFormat.RAW

        # With oversampling -> AVERAGED format
        adc2 = TLA2528(
            bus=mock_bus,
            oversampling_ratio=OversamplingRatio.OSR_16,
            auto_init=False,
        )
        assert adc2._data_format == DataFormat.AVERAGED


class TestConversions:
    """Test ADC value conversions."""

    def test_raw_to_mv_12bit(self):
        """Test 12-bit raw to mV conversion."""
        mock_bus = Mock()
        mock_bus.write_i2c_block_data = Mock()
        mock_bus.read_byte = Mock(return_value=0)

        adc = TLA2528(
            bus=mock_bus,
            avdd_volts=3.3,
            oversampling_ratio=OversamplingRatio.NONE,
            auto_init=False,
        )

        # Test conversions
        assert adc._raw_to_mv(0) == 0.0
        assert abs(adc._raw_to_mv(4095) - 3300.0) < 0.1  # Full scale
        assert abs(adc._raw_to_mv(2048) - 1650.0) < 1.0  # Mid scale

    def test_raw_to_mv_16bit(self):
        """Test 16-bit raw to mV conversion."""
        mock_bus = Mock()
        mock_bus.write_i2c_block_data = Mock()
        mock_bus.read_byte = Mock(return_value=0)

        adc = TLA2528(
            bus=mock_bus,
            avdd_volts=3.3,
            oversampling_ratio=OversamplingRatio.OSR_16,
            auto_init=False,
        )

        # Test conversions
        assert adc._raw_to_mv(0) == 0.0
        assert abs(adc._raw_to_mv(65535) - 3300.0) < 0.1  # Full scale
        assert abs(adc._raw_to_mv(32768) - 1650.0) < 1.0  # Mid scale


class TestChannelValidation:
    """Test channel validation."""

    def test_analog_channel_validation(self):
        """Test analog input channel validation."""
        mock_bus = Mock()
        mock_bus.write_i2c_block_data = Mock()
        mock_bus.read_byte = Mock(return_value=0)

        adc = TLA2528(
            bus=mock_bus,
            analog_inputs=[Channel.CH0],
            digital_inputs=[Channel.CH1],
            auto_init=False,
        )

        # Verify channel is analog
        assert adc._is_analog_input(Channel.CH0)
        assert not adc._is_analog_input(Channel.CH1)

    def test_digital_input_validation(self):
        """Test digital input channel validation."""
        mock_bus = Mock()
        mock_bus.write_i2c_block_data = Mock()
        mock_bus.read_byte = Mock(return_value=0)

        adc = TLA2528(
            bus=mock_bus,
            digital_inputs=[Channel.CH2],
            auto_init=False,
        )

        assert adc._is_digital_input(Channel.CH2)
        assert not adc._is_digital_input(Channel.CH0)

    def test_digital_output_validation(self):
        """Test digital output channel validation."""
        mock_bus = Mock()
        mock_bus.write_i2c_block_data = Mock()
        mock_bus.read_byte = Mock(return_value=0)

        adc = TLA2528(
            bus=mock_bus,
            digital_outputs=[Channel.CH3],
            auto_init=False,
        )

        assert adc._is_digital_output(Channel.CH3)
        assert not adc._is_digital_output(Channel.CH0)


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_channel_for_analog_read(self):
        """Test reading from non-analog channel raises error."""
        mock_bus = Mock()
        mock_bus.write_i2c_block_data = Mock()
        mock_bus.read_byte = Mock(return_value=0)

        adc = TLA2528(
            bus=mock_bus,
            analog_inputs=[Channel.CH0],
            digital_inputs=[Channel.CH1],
            auto_init=False,
        )

        # Should raise error when trying to read digital channel as analog
        with pytest.raises(InvalidChannelError):
            adc._trigger_conversion(Channel.CH1)

    def test_manual_mode_read_all_error(self):
        """Test read_all raises error in MANUAL mode."""
        mock_bus = Mock()
        mock_bus.write_i2c_block_data = Mock()
        mock_bus.read_byte = Mock(return_value=0)

        adc = TLA2528(
            bus=mock_bus,
            mode=Mode.MANUAL,
            analog_inputs=[Channel.CH0, Channel.CH1],
            auto_init=False,
        )

        # read_all requires AUTO_SEQ mode
        with pytest.raises(ConfigurationError):
            adc._read_all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
