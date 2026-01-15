#!/usr/bin/env python3
"""Basic example: Read analog inputs from TLA2528 ADC."""

import time
from tla2528 import TLA2528, Channel, OversamplingRatio

# Initialize the ADC
# - I2C bus 1 (default on Raspberry Pi)
# - Default address 0x10
# - Configure channels 0, 1, 2 as analog inputs
# - Use 16x oversampling for better precision
adc = TLA2528(
    bus=1,
    address=0x10,
    avdd_volts=3.3,  # Reference voltage
    analog_inputs=[Channel.CH0, Channel.CH1, Channel.CH2],
    oversampling_ratio=OversamplingRatio.OSR_16,
    auto_calibrate=True,  # Calibrate on startup
)

print("TLA2528 ADC - Basic Reading Example")
print("=" * 40)
print("Reading channels 0, 1, 2...")
print()

try:
    while True:
        # Read individual channels
        ch0_mv = adc.get_mv(Channel.CH0)
        ch1_mv = adc.get_mv(Channel.CH1)
        ch2_mv = adc.get_mv(Channel.CH2)

        print(f"CH0: {ch0_mv:7.2f} mV  |  CH1: {ch1_mv:7.2f} mV  |  CH2: {ch2_mv:7.2f} mV")

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nExiting...")
