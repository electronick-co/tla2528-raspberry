# Installation Guide

## For Users (from PyPI)

Once published to PyPI, install with:

```bash
pip install tla2528
```

## For Developers (from source)

### 1. Clone or Download

```bash
cd /home/raspberry/Documents/tla2528_port
```

### 2. Install in Development Mode

```bash
# Install in editable mode with dependencies
pip install -e .

# Or with development dependencies (for testing)
pip install -e ".[dev]"
```

### 3. Verify Installation

```python
python3 -c "from tla2528 import TLA2528; print('Success!')"
```

## System Requirements

### Hardware
- Raspberry Pi (or any Linux system with I2C)
- TLA2528 ADC connected via I2C

### Software
- Python 3.8 or higher
- I2C enabled on your system

### Enable I2C on Raspberry Pi

```bash
# Using raspi-config
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable

# Or edit config directly
sudo bash -c 'echo "dtparam=i2c_arm=on" >> /boot/config.txt'
sudo reboot
```

### Verify I2C Access

```bash
# List I2C buses
ls -l /dev/i2c*

# Scan for devices on bus 1
sudo i2cdetect -y 1
```

### I2C Permissions

Add your user to the `i2c` group:

```bash
sudo usermod -a -G i2c $USER
# Log out and back in for changes to take effect
```

## Building Distribution Packages

### Build wheel and source distribution

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# This creates:
# - dist/tla2528-0.1.0-py3-none-any.whl
# - dist/tla2528-0.1.0.tar.gz
```

### Install from local build

```bash
pip install dist/tla2528-0.1.0-py3-none-any.whl
```

## Publishing to PyPI

### Test on TestPyPI first

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Install from TestPyPI to test
pip install --index-url https://test.pypi.org/simple/ tla2528
```

### Publish to PyPI

```bash
# Upload to PyPI (requires account and API token)
python -m twine upload dist/*
```

### Setup PyPI credentials

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest --cov=tla2528 tests/
```

## Troubleshooting

### ImportError: No module named 'smbus2'

```bash
pip install smbus2
```

### Permission denied: '/dev/i2c-1'

```bash
sudo usermod -a -G i2c $USER
# Log out and back in
```

### OSError: [Errno 2] No such file or directory: '/dev/i2c-1'

I2C is not enabled. Follow the "Enable I2C" steps above.

### ModuleNotFoundError: No module named 'tla2528'

Make sure you installed the package:
```bash
pip install -e .
```
