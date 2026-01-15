#!/usr/bin/env python3
"""Example: Use digital I/O functionality of TLA2528."""

import time
from tla2528 import TLA2528, Channel, OutputMode

# Configure some channels as analog, some as digital I/O
adc = TLA2528(
    bus=1,
    address=0x10,
    avdd_volts=3.3,
    analog_inputs=[Channel.CH0, Channel.CH1],  # Analog inputs
    digital_inputs=[Channel.CH2, Channel.CH3],  # Digital inputs
    digital_outputs=[Channel.CH4, Channel.CH5],  # Digital outputs
    digital_output_modes={
        Channel.CH4: OutputMode.PUSH_PULL,
        Channel.CH5: OutputMode.OPEN_DRAIN,
    },
    digital_output_values={
        Channel.CH4: False,  # Start low
        Channel.CH5: False,
    },
)

print("TLA2528 - Digital I/O Example")
print("=" * 40)
print("Configuration:")
print("  - CH0, CH1: Analog inputs")
print("  - CH2, CH3: Digital inputs")
print("  - CH4: Digital output (push-pull)")
print("  - CH5: Digital output (open-drain)")
print()

try:
    led_state = False
    while True:
        # Toggle digital outputs
        led_state = not led_state
        adc.set_digital_output_value(Channel.CH4, led_state)
        adc.set_digital_output_value(Channel.CH5, led_state)

        # Read digital inputs
        din2 = adc.get_digital_input_value(Channel.CH2)
        din3 = adc.get_digital_input_value(Channel.CH3)

        # Read analog inputs
        ain0 = adc.get_mv(Channel.CH0)
        ain1 = adc.get_mv(Channel.CH1)

        print(f"Outputs: CH4={led_state:1d} CH5={led_state:1d}  |  "
              f"Inputs: CH2={din2:1d} CH3={din3:1d}  |  "
              f"Analog: CH0={ain0:6.1f}mV CH1={ain1:6.1f}mV")

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nExiting...")
    # Turn off outputs
    adc.set_digital_output_value(Channel.CH4, False)
    adc.set_digital_output_value(Channel.CH5, False)
