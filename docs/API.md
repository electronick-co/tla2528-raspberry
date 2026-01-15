# TLA2528 API Documentation

## Class: TLA2528

Main class for interfacing with TLA2528 ADC.

### Constructor

```python
TLA2528(
    bus: Union[int, SMBus],
    address: int = 0x10,
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
)
```

#### Parameters

- **bus**: I2C bus number (e.g., 1 for `/dev/i2c-1`) or SMBus instance
- **address**: I2C device address (default: 0x10)
- **avdd_volts**: AVDD reference voltage in volts (default: 3.3)
- **mode**: Sampling mode (MANUAL or AUTO_SEQ)
- **analog_inputs**: List of channels configured as analog inputs
- **digital_inputs**: List of channels configured as digital inputs
- **digital_outputs**: List of channels configured as digital outputs
- **digital_output_modes**: Optional dict mapping channels to OutputMode
- **digital_output_values**: Optional dict with initial output values
- **oversampling_ratio**: Oversampling ratio (NONE to OSR_128)
- **append**: Data to append to readings (NONE or CHANNEL_ID)
- **auto_init**: Automatically initialize device (default: True)
- **auto_calibrate**: Automatically calibrate after init (default: False)
- **log_level**: Python logging level (default: logging.WARNING)

### Methods

#### initialize()

```python
def initialize() -> None
```

Initialize the ADC with configured settings. Called automatically if `auto_init=True`.

**Raises**: `I2CError`, `ConfigurationError`

---

#### calibrate()

```python
def calibrate(poll_interval: float = 0.010, timeout: float = 0.100) -> None
```

Calibrate the ADC for improved accuracy.

**Parameters**:
- `poll_interval`: Time between status polls (seconds)
- `timeout`: Maximum time to wait (seconds)

**Raises**: `TimeoutError`, `I2CError`

---

#### get_mv()

```python
def get_mv(channel: Channel) -> float
```

Read voltage from a single analog channel.

**Parameters**:
- `channel`: Channel to read (Channel.CH0 to Channel.CH7)

**Returns**: Voltage in millivolts (float)

**Raises**: `InvalidChannelError`, `I2CError`

**Example**:
```python
voltage = adc.get_mv(Channel.CH0)
print(f"CH0: {voltage:.2f} mV")
```

---

#### get_all_mv()

```python
def get_all_mv() -> List[float]
```

Read voltages from all configured analog channels. Requires AUTO_SEQ mode.

**Returns**: List of voltages in millivolts (in order of `analog_inputs`)

**Raises**: `ConfigurationError`, `I2CError`

**Example**:
```python
voltages = adc.get_all_mv()
for i, v in enumerate(voltages):
    print(f"Channel {i}: {v:.2f} mV")
```

---

#### get_all_mv_map()

```python
def get_all_mv_map() -> Dict[Channel, float]
```

Read voltages from all configured channels as a dictionary.

**Returns**: Dict mapping Channel to voltage in millivolts

**Raises**: `ConfigurationError`, `I2CError`

**Example**:
```python
voltages = adc.get_all_mv_map()
print(f"CH0: {voltages[Channel.CH0]:.2f} mV")
```

---

#### set_digital_output_mode()

```python
def set_digital_output_mode(channel: Channel, output_mode: OutputMode) -> None
```

Configure digital output mode for a channel.

**Parameters**:
- `channel`: Channel to configure
- `output_mode`: OutputMode.OPEN_DRAIN or OutputMode.PUSH_PULL

**Raises**: `InvalidChannelError`, `I2CError`

---

#### set_digital_output_value()

```python
def set_digital_output_value(channel: Channel, value: bool) -> None
```

Set digital output value.

**Parameters**:
- `channel`: Channel to set
- `value`: True=high, False=low

**Raises**: `InvalidChannelError`, `I2CError`

---

#### get_digital_input_value()

```python
def get_digital_input_value(channel: Channel) -> bool
```

Read digital input value from a channel.

**Parameters**:
- `channel`: Channel to read

**Returns**: True=high, False=low

**Raises**: `InvalidChannelError`, `I2CError`

---

#### get_digital_input_values()

```python
def get_digital_input_values() -> int
```

Read all digital input values as a bitfield.

**Returns**: 8-bit value (LSB=CH0, MSB=CH7)

**Raises**: `I2CError`

---

#### reset()

```python
def reset() -> None
```

Perform software reset. Resets all registers to default values.

**Raises**: `I2CError`

---

## Enumerations

### Channel

```python
class Channel(IntEnum):
    CH0 = 0
    CH1 = 1
    CH2 = 2
    CH3 = 3
    CH4 = 4
    CH5 = 5
    CH6 = 6
    CH7 = 7
```

### OversamplingRatio

```python
class OversamplingRatio(IntEnum):
    NONE = 0     # No oversampling (12-bit)
    OSR_2 = 1    # 2x oversampling
    OSR_4 = 2    # 4x oversampling
    OSR_8 = 3    # 8x oversampling
    OSR_16 = 4   # 16x oversampling
    OSR_32 = 5   # 32x oversampling
    OSR_64 = 6   # 64x oversampling
    OSR_128 = 7  # 128x oversampling (16-bit)
```

### Mode

```python
class Mode(IntEnum):
    MANUAL = 0    # Manual mode (host controls conversions)
    AUTO_SEQ = 1  # Auto-sequence mode (automatic scanning)
```

### OutputMode

```python
class OutputMode(IntEnum):
    OPEN_DRAIN = 0  # Open-drain output
    PUSH_PULL = 1   # Push-pull output
```

### DataFormat

```python
class DataFormat(IntEnum):
    RAW = 0       # 12-bit raw data
    AVERAGED = 1  # 16-bit averaged data
```

### Append

```python
class Append(IntEnum):
    NONE = 0       # No additional data
    CHANNEL_ID = 1 # Append 4-bit channel ID
```

---

## Exceptions

All exceptions inherit from `TLA2528Error`.

- **TLA2528Error**: Base exception
- **I2CError**: I2C communication failure
- **ConfigurationError**: Invalid configuration
- **TimeoutError**: Operation timed out
- **CalibrationError**: Calibration failed
- **InvalidChannelError**: Channel not configured for operation

---

## Examples

### Basic Usage

```python
from tla2528 import TLA2528, Channel

adc = TLA2528(bus=1, analog_inputs=[Channel.CH0, Channel.CH1])
voltage = adc.get_mv(Channel.CH0)
print(f"Voltage: {voltage:.2f} mV")
```

### High Precision Reading

```python
from tla2528 import TLA2528, Channel, OversamplingRatio

adc = TLA2528(
    bus=1,
    analog_inputs=[Channel.CH0],
    oversampling_ratio=OversamplingRatio.OSR_128,
    auto_calibrate=True
)
voltage = adc.get_mv(Channel.CH0)
```

### Auto-Sequence Mode

```python
from tla2528 import TLA2528, Channel, Mode

adc = TLA2528(
    bus=1,
    mode=Mode.AUTO_SEQ,
    analog_inputs=[Channel.CH0, Channel.CH1, Channel.CH2, Channel.CH3]
)
voltages = adc.get_all_mv()
```

### Digital I/O

```python
from tla2528 import TLA2528, Channel, OutputMode

adc = TLA2528(
    bus=1,
    digital_inputs=[Channel.CH0],
    digital_outputs=[Channel.CH1],
    digital_output_modes={Channel.CH1: OutputMode.PUSH_PULL}
)

# Set output
adc.set_digital_output_value(Channel.CH1, True)

# Read input
value = adc.get_digital_input_value(Channel.CH0)
```
