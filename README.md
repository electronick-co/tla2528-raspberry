# TLA2528 Python Library

Python library for interfacing with the TLA2528 family of ADC chips on Linux (Raspberry Pi).

## Overview

The TLA2528 is a 12/16-bit, 8-channel ADC with 8 digital I/O pins. It supports:
- Manual and auto-sequence sampling modes
- Oversampling ratios (2x, 4x, 8x, 16x, 32x, 64x, 128x)
- Configurable analog and digital I/O
- Alert triggers based on voltage thresholds

**Datasheet**: https://www.ti.com/lit/ds/symlink/tla2528.pdf

## Installation

```bash
pip install tla2528
```

## Quick Start

```python
from tla2528 import TLA2528, Channel, OversamplingRatio

# Initialize the ADC
adc = TLA2528(
    bus=1,  # I2C bus number
    address=0x10,  # Default I2C address
    avdd_volts=3.3,
    analog_inputs=[Channel.CH0, Channel.CH1, Channel.CH2],
    oversampling_ratio=OversamplingRatio.OSR_16
)

# Read single channel
voltage_mv = adc.get_mv(Channel.CH0)
print(f"Channel 0: {voltage_mv:.2f} mV")

# Read all configured channels
voltages = adc.get_all_mv()
for i, voltage in enumerate(voltages):
    print(f"Channel {i}: {voltage:.2f} mV")
```

## Features

- ✅ Manual and Auto-Sequence ADC reading modes
- ✅ Oversampling for increased precision
- ✅ Digital input/output configuration
- ✅ Automatic calibration support
- ✅ Thread-safe operations
- ✅ Comprehensive error handling

## Requirements

- Python 3.8+
- Linux with I2C support (Raspberry Pi, etc.)
- `smbus2` library

## Hardware Connection

Connect the TLA2528 to your Raspberry Pi I2C bus:
- VDD → 3.3V
- GND → Ground
- SDA → I2C SDA (GPIO 2)
- SCL → I2C SCL (GPIO 3)

Enable I2C on Raspberry Pi:
```bash
sudo raspi-config
# Interface Options → I2C → Enable
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
