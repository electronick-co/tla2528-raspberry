# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python library for interfacing with the TLA2528 ADC chip on Linux/Raspberry Pi. It was ported from a C++/ESP32 implementation and provides I2C-based communication with the 12/16-bit, 8-channel ADC.

**Hardware**: TLA2528 ADC (Texas Instruments)
**Platform**: Linux with I2C support (primarily Raspberry Pi)
**Datasheet**: https://www.ti.com/lit/ds/symlink/tla2528.pdf

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Building
```bash
# Build distribution packages
python -m build

# Output: dist/tla2528-0.1.0-py3-none-any.whl
#         dist/tla2528-0.1.0.tar.gz
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=tla2528 tests/

# Run a single test file
pytest tests/test_basic.py -v

# Run a specific test
pytest tests/test_basic.py::TestConversions::test_raw_to_mv_12bit -v
```

### Running Examples
```bash
# All examples are executable
python3 examples/basic_reading.py
python3 examples/auto_sequence_mode.py
python3 examples/digital_io.py
python3 examples/simple_voltmeter.py
```

### Publishing
```bash
# Test on TestPyPI first
python -m twine upload --repository testpypi dist/*

# Publish to PyPI
python -m twine upload dist/*
```

## Architecture

### Module Structure

**`src/tla2528/`** - Main package organized into 5 modules:

1. **`tla2528.py`** (625 lines) - Main `TLA2528` class
   - Manages I2C communication via SMBus
   - Thread-safe operations using `RLock`
   - Handles initialization, calibration, ADC reading, and digital I/O
   - All I2C operations go through low-level methods: `_read_one()`, `_write_one()`, `_set_bits()`, `_clear_bits()`

2. **`registers.py`** - Hardware register definitions
   - `Register` enum: Register addresses (e.g., `SYSTEM_STATUS`, `GENERAL_CFG`)
   - `Opcode` class: I2C opcodes (e.g., `READ_ONE`, `WRITE_ONE`, `SET_BITS`)
   - Bit mask classes: `SystemStatusBits`, `GeneralCfgBits`, etc.

3. **`enums.py`** - User-facing enumerations
   - `Channel` (CH0-CH7)
   - `OversamplingRatio` (NONE, OSR_2 through OSR_128)
   - `Mode` (MANUAL, AUTO_SEQ)
   - `OutputMode`, `DataFormat`, `Append`

4. **`exceptions.py`** - Exception hierarchy
   - Base: `TLA2528Error`
   - Specific: `I2CError`, `ConfigurationError`, `TimeoutError`, `CalibrationError`, `InvalidChannelError`

5. **`__init__.py`** - Package exports and version

### Key Design Patterns

**I2C Communication Layer**:
- Uses `smbus2.SMBus` for Linux I2C
- TLA2528 has custom protocol with opcodes (not standard register read/write)
- Example: Reading a register requires sending `[OP_READ_ONE, register_addr]` then reading response

**Two Operating Modes**:
- **MANUAL**: Host triggers each conversion, reads one channel at a time
- **AUTO_SEQ**: Device automatically scans configured channels

**Data Format Selection**:
- Without oversampling → 12-bit RAW format
- With oversampling → 16-bit AVERAGED format
- Automatically set based on `oversampling_ratio` parameter

**Channel Configuration**:
Each of 8 channels can be independently configured as:
- Analog input (ADC reading)
- Digital input (GPIO read)
- Digital output (GPIO write with push-pull or open-drain)

**Thread Safety**:
- All public methods acquire `self._lock` (RLock)
- Safe for multi-threaded access to same ADC instance

### Porting Notes (C++ → Python)

Original implementation was for ESP32 in C++. Key translations:
- `std::mutex` → `threading.RLock`
- `std::error_code` → Custom exceptions
- `BasePeripheral` base class → Direct SMBus integration
- `espp::Logger` → Python `logging` module
- `std::vector<Channel>` → `List[Channel]`
- `std::unordered_map` → `Dict`

The C++ version is in `tla2528.hpp` (reference only).

## Working with Hardware Registers

The TLA2528 has a non-standard I2C protocol:

**Reading a register**:
```python
# Internally: write [OP_READ_ONE, reg_addr], then read 1 byte
value = self._read_one(Register.SYSTEM_STATUS)
```

**Writing a register**:
```python
# Internally: write [OP_WRITE_ONE, reg_addr, value]
self._write_one(Register.OSR_CFG, 0x04)
```

**Setting specific bits** (without modifying others):
```python
# Internally: write [OP_SET_BITS, reg_addr, bit_mask]
self._set_bits(Register.GENERAL_CFG, GeneralCfgBits.CAL)
```

**Clearing specific bits**:
```python
# Internally: write [OP_CLR_BITS, reg_addr, bit_mask]
self._clear_bits(Register.SEQUENCE_CFG, SequenceCfgBits.SEQ_START)
```

## Testing Without Hardware

Tests use mocked SMBus objects:
```python
mock_bus = Mock()
mock_bus.write_i2c_block_data = Mock()
mock_bus.read_byte = Mock(return_value=0)

adc = TLA2528(bus=mock_bus, auto_init=False)
```

The `auto_init=False` parameter prevents I2C communication during construction.

## Known Limitations

- **Platform**: Linux only (requires `/dev/i2c-*`)
- **Alert Pin**: Not yet implemented (future enhancement)
- **Event Handling**: Not yet implemented
- **Async Support**: Synchronous only (no async/await)

## Common Modification Patterns

**Adding a new register operation**:
1. Add register address to `Register` enum in `registers.py`
2. Add bit masks to appropriate class (e.g., `SystemStatusBits`)
3. Add method to `TLA2528` class using `_read_one()`/`_write_one()`

**Adding a new feature**:
1. Add enum values to `enums.py` if needed
2. Add exception type to `exceptions.py` if needed
3. Implement in `TLA2528` class with proper locking
4. Add test to `tests/test_basic.py`
5. Add example to `examples/`

**Updating for new hardware variant**:
- TLA2528 family includes TLA2521, TLA2524, etc. (different channel counts)
- Channel count is not enforced - configurable via `analog_inputs` parameter
- Default I2C address varies by variant (check datasheet Table 2)

## Version and Dependencies

- **Python**: 3.8+ required (uses type hints)
- **Required**: `smbus2>=0.4.0`
- **Optional dev**: `pytest`, `pytest-cov`, `black`, `flake8`, `mypy`
- **Current version**: 0.1.0 (alpha status)
