# TLA2528 Examples

This directory contains example scripts demonstrating various features of the TLA2528 library.

## Prerequisites

1. Enable I2C on your Raspberry Pi:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → I2C → Enable
   ```

2. Install the library:
   ```bash
   pip install tla2528
   ```

3. Connect your TLA2528 to the Raspberry Pi I2C bus:
   - VDD → 3.3V
   - GND → Ground
   - SDA → GPIO 2 (Pin 3)
   - SCL → GPIO 3 (Pin 5)

## Examples

### basic_reading.py
Simple example reading from 3 analog channels with oversampling.

```bash
python3 basic_reading.py
```

### auto_sequence_mode.py
Demonstrates auto-sequence mode for efficient multi-channel reading.

```bash
python3 auto_sequence_mode.py
```

### digital_io.py
Shows how to use digital input and output functionality alongside analog inputs.

```bash
python3 digital_io.py
```

### simple_voltmeter.py
A simple voltmeter application with maximum precision settings.

```bash
python3 simple_voltmeter.py
```

## Troubleshooting

### Permission Denied
If you get permission errors accessing I2C:
```bash
sudo usermod -a -G i2c $USER
# Log out and back in
```

### Device Not Found
Check I2C devices:
```bash
sudo i2cdetect -y 1
```

You should see your device at address 0x10 (or your configured address).

### Import Errors
Make sure the library is installed:
```bash
pip install -e /path/to/tla2528
```
