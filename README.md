    i2c driver to the IS31FL3197 chip
    datasheet: https://www.lumissil.com/assets/pdf/core/IS31FL3197_DS.pdf
    
    this chip can be found on the arduino giga display shield
    this driver was developed and tested using openMV

    the is31fl3197 can drive 4 leds: red ('R'), green ()'G'), blue ('B') and a white ('W')

    on the giga display shield, only leds R, G and B are populated, led W is not
    see https://docs.arduino.cc/resources/schematics/ASX00039-schematics.pdf 
    
    any code for the white led is untested (though the code is there and marked as untested)

    the chip offers 3 modes of operation for each led individually:
    - pwm & current source mode
    - pattern mode
    - current source mode

    this driver offers 3 interfaces:
    - led: direct control of individual leds
    - color: grouped control of all leds with color tuples
    - pattern: grouped sequences of colors with humanized parameters

    the chip allows each LED individually to be in any mode at anytime
    - this driver assumes either led, color or pattern mode
    - modus color and modus pattern preset the modus for ALL leds simutaneously, overwriting individual settings 
    - modus led presets modus for individual leds
    - so: AFTER setting modus color or pattern, individual leds can be overwritten to be configured differently (not the other way round) 
    - setting properties directly will lead to inconsistent modes
    
    intensity and color patterns can run in deep sleep mode of the controlling MCU
    this offers the possibility of end-user feedback with minimal MCU power consumption or while executing blokcing code

    not implemented: 
    - shutdown control register settings (0x01)
    - charge pump settings (0x3, 0x4)

    version information:
    at times of testing: OpenMV 4.5.9
