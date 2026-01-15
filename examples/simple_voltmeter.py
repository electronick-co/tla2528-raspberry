#!/usr/bin/env python3
"""Example: Simple voltmeter using TLA2528."""

import time
from tla2528 import TLA2528, Channel, OversamplingRatio

print("TLA2528 Simple Voltmeter")
print("=" * 40)
print("Connect voltage to measure to CH0")
print("(Max voltage: 3.3V)")
print()

# Initialize with highest precision
adc = TLA2528(
    bus=1,
    address=0x10,
    avdd_volts=3.3,
    analog_inputs=[Channel.CH0],
    oversampling_ratio=OversamplingRatio.OSR_128,  # Maximum oversampling
    auto_calibrate=True,  # Calibrate for best accuracy
)

try:
    # Take multiple readings and average for stability
    num_samples = 10

    while True:
        readings = []
        for _ in range(num_samples):
            readings.append(adc.get_mv(Channel.CH0))
            time.sleep(0.01)

        avg_mv = sum(readings) / len(readings)
        avg_v = avg_mv / 1000.0

        # Simple bar graph
        bar_length = int(avg_v / 3.3 * 30)
        bar = "█" * bar_length + "░" * (30 - bar_length)

        print(f"Voltage: {avg_v:5.3f} V  ({avg_mv:7.2f} mV)  [{bar}]", end="\r")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nExiting...")
