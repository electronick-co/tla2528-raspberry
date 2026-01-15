# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-14

### Added
- Initial release of TLA2528 Python library
- Full support for TLA2528 ADC on Linux/Raspberry Pi (ported from C++/ESP32)
- I2C communication via SMBus
- Manual and Auto-Sequence ADC reading modes
- 8-channel analog input support (12-bit and 16-bit modes)
- Oversampling support (2x, 4x, 8x, 16x, 32x, 64x, 128x)
- Digital I/O functionality (input and output)
- Push-pull and open-drain output modes
- Automatic calibration support
- Thread-safe operations using RLock
- Comprehensive error handling with custom exceptions
- Type hints throughout for better IDE support
- Complete API documentation
- Example scripts:
  - Basic analog reading
  - Auto-sequence mode
  - Digital I/O control
  - Simple voltmeter application
- Unit tests with pytest
- Support for Python 3.8+

### Features
- Read voltage from single or multiple channels
- Configure channels as analog inputs, digital inputs, or digital outputs
- Automatic data format selection based on oversampling ratio
- Register-level access for advanced operations
- Voltage conversion (raw ADC values to millivolts)
- Software reset capability

### Documentation
- README with quick start guide
- Complete API reference (API.md)
- Installation guide (INSTALL.md)
- CLAUDE.md for AI-assisted development
- Porting summary documenting C++ to Python translation

### Dependencies
- Python 3.8 or higher
- smbus2 >= 0.4.0

### Known Limitations
- Linux only (requires `/dev/i2c-*`)
- Alert pin functionality not yet implemented
- Event-driven reading not yet implemented
- Synchronous only (no async/await support)

[0.1.0]: https://github.com/electronick-co/tla2528-raspberry/releases/tag/v0.1.0
