#!/usr/bin/env python3
"""Example: Use auto-sequence mode to read multiple channels efficiently."""

import time
from tla2528 import TLA2528, Channel, Mode, OversamplingRatio

# Initialize in AUTO_SEQ mode for faster multi-channel reading
adc = TLA2528(
    bus=1,
    address=0x10,
    avdd_volts=3.3,
    mode=Mode.AUTO_SEQ,  # Auto-sequence mode
    analog_inputs=[
        Channel.CH0,
        Channel.CH1,
        Channel.CH2,
        Channel.CH3,
        Channel.CH4,
    ],
    oversampling_ratio=OversamplingRatio.OSR_32,
    auto_calibrate=True,
)

print("TLA2528 ADC - Auto-Sequence Mode Example")
print("=" * 50)
print("Reading 5 channels in auto-sequence mode...")
print()

try:
    while True:
        # Read all channels at once (more efficient in AUTO_SEQ mode)
        voltages = adc.get_all_mv()

        # Display as list
        print("Voltages (mV):", end=" ")
        for i, voltage in enumerate(voltages):
            print(f"CH{i}:{voltage:7.2f}", end=" | ")
        print()

        # Or use dictionary format
        voltage_map = adc.get_all_mv_map()
        print("As dictionary:", voltage_map)
        print()

        time.sleep(1.0)

except KeyboardInterrupt:
    print("\nExiting...")
