# I2C Driver for the IS31FL3197 Chip

## Overview

This repository contains an I2C driver for the [IS31FL3197 chip](https://www.lumissil.com/assets/pdf/core/IS31FL3197_DS.pdf). The chip can for instance be found on the Arduino GIGA Display Shield. This driver was developed and tested using OpenMV on an Arduino Giga R1 Wifi with the shield attached.

The IS31FL3197 can drive four LEDs:

- Red (`R`)
- Green (`G`)
- Blue (`B`)
- White (`W`)

On the GIGA Display Shield, only the `R`, `G`, and `B` LEDs are populated. The `W` LED is not populated. See the [schematics](https://docs.arduino.cc/resources/schematics/ASX00039-schematics.pdf) for more information.

> **Note:** Any code for the white LED (`W`) is untested, though the code is present and marked as such.

## Chip Modes

The IS31FL3197 offers three modes of operation for each LED individually:

- **PWM & Current Source Mode**
- **Pattern Mode**
- **Current Source Mode**

## Driver Interfaces

This driver provides three interfaces:

1. **LED:** Direct control of individual LEDs.
2. **Color:** Grouped control of all LEDs with color tuples.
3. **Pattern:** Grouped sequences of colors with humanized parameters.

## Mode Configuration

Each LED can be in any mode at any time. The driver assumes one of three modes:

- **Color Mode:** Sets the mode for all LEDs simultaneously.
- **Pattern Mode:** Sets the mode for all LEDs simultaneously.
- **LED Mode:** Sets the mode for individual LEDs.

### Important Notes:

- Setting **color** or **pattern** mode presets the mode for **all LEDs**, overwriting individual settings.
- After setting **color** or **pattern** mode, individual LEDs can be reconfigured.
- Setting properties directly without considering the mode may lead to inconsistent configurations.

## Power Efficiency

Intensity and color patterns can run in the deep sleep mode of the controlling MCU, allowing for end-user feedback with minimal power consumption or while executing blocking code.

## Not Implemented

- Shutdown control register settings (0x01)
- Charge pump settings (0x03, 0x04)

## Version Information

- Tested with OpenMV 4.5.9

## Usage Examples

### Initialization

```python
is31 = IS31FL3197(80)  # I2C address for the Arduino GIGA Display Shield is 80
```

### Individual LED Interface (Red LED)

```python
is31.r.on()             # Fully on (intensity 255)
is31.r.intensity(64)    # Intensity: 0..255
is31.r.pwm(1023)        # PWM: 0..4095
is31.r.clb(1)           # Current Level Boost: 1..4
is31.r.dim(50)          # Dim: 0..100%
is31.r.off()            # Fully off
```

### Grouped LEDs in Color Interface

```python
is31.rgb.color(RED)     # Set color (0..255, 0..255, 0..255)
is31.rgb.pwm(1023)      # PWM: 0..4095
is31.rgb.clb(1)         # Current Level Boost: 1..4
is31.rgb.off()          # Turn off
```

### Grouped Colors in Pattern Interface

```python
is31.pattern.config(
    start_time=0.,               # Start time in seconds (0-10s)
    rise_time=0.,
    hold_time=0.,
    fall_time=0.,
    between_time=0.,
    off_time=0.,
    crossfade_time=0.,
    crossfade=False,            # Crossfade: True or False
    gamma='2.4',                # Gamma options: '2.4', '3.5', or 'linear'
    cycles_1=1,                 # Cycles: 1..3 or 'endless' (maps to 0)
    cycles_2=1,
    cycles_3=1,
    multi_pulse_loops=1,        # Multi-pulse loops: 1..15 or 'endless' (maps to 0)
    pattern_loops=64,           # Pattern loops: 1..64 or 'endless' (maps to 0)
    times16=True,               # Multiply pattern_loops (max 1024)
    hold_time_selection='T4',   # Hold time selection: 'T4' or 'T2'
    hold_time_function=False,
    color_1=RED,
    color_2=GREEN,
    color_3=BLUE,
    activate=True
)
is31.pattern.stop()
is31.pattern.clb(1)                         # Current Level Boost: 1..4
is31.pattern.start()
```

### Pattern State Monitoring

```python
is31.pattern.monitor(10)  # Monitor pattern state for a period in seconds
```

