import machine, time
from machine import I2C

class IS31FL3197:
    '''
    i2c driver to the IS31FL3197 chip
    datasheet: https://www.lumissil.com/assets/pdf/core/IS31FL3197_DS.pdf

    the is31fl3197 can drive 4 leds: red ('R'), green ()'G'), blue ('B') and a white ('W')
    
    this chip can be found on the arduino giga display shield
    this driver was developed and tested using openMV

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

    sample use in test_IS31FL3197.py

    ----- license -----

    MIT No Attribution

    Copyright (c) 2025 Erik de Ruijter, Eindhoven

    Permission is hereby granted, free of charge, to any person obtaining a copy of this
    software and associated documentation files (the "Software"), to deal in the Software
    without restriction, including without limitation the rights to use, copy, modify,
    merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
    PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    '''

    class _led:
        '''
        interface to indivisual leds
        only to be instantiated class IS31FL3197 
        '''
        def __init__(self, chip, scope):
            self._chip = chip
            self._scope = scope
            self._intensity = 0

        def on(self):
            '''
            intensity, pwm and current band to the max
            '''
            self._intensity = 255
            self._chip._config_led(self._intensity, 4095, 4, self._scope)

        def off(self):
            '''
            intensity, pwm, current band to the min 
            '''
            self._intensity = 0
            self._chip._config_led(self._intensity, 0, 1, self._scope)

        def intensity(self, intensity_setting):
            '''
            0..255
            '''
            self._intensity = intensity_setting
            self._chip._config_intensity(self._intensity, self._scope)

        def pwm(self, duty_cycle):
            '''
            0..4095
            '''
            self._chip._config_pwm(duty_cycle, self._scope)

        def clb(self, band):
            '''
            1..4 = 1/4 to 4/4, or 25% to 100%
            '''
            self._chip._config_current_limit_band(band, self._scope)

        def dim(self, percentage):
            self._intensity = int(self._intensity * percentage/100)
            self._chip._config_intensity(self._intensity, self._scope)

    class _rgb:
        '''
        interface to colors
        only to be instantiated class IS31FL3197 
        '''
        def __init__(self, chip, scope):
            self._chip = chip
            self._scope = scope
            self._color = (0, 0, 0)

        def color(self, color_tuple):
            '''
            pwm and current band to the max
            '''
            self._color = color_tuple
            self._chip._config_color(self._color, 4095, 4)

        def pwm(self, duty_cycle):
            '''
            0..4095
            '''
            self._chip._config_pwm(duty_cycle, self._scope)

        def off(self):
            '''
            color to black, pwm and current band to the min
            '''
            self._color = (0, 0, 0)
            self._chip._config_color(self._color, 0, 1)

        def clb(self, band):
            '''
            1..4 = 1/4 to 4/4, or 25% to 100%
            '''
            self._chip._config_current_limit_band(band, self._scope)

        def dim(self, percentage):
            '''
            0..100% on whatever the intensity setting is
            '''
            for i in range (3):
                self._color[i] = int(self._color[i] * percentage/100)
            self._chip._config_intensity(self._color, self._scope)

    class _pattern:
        '''
        interface to patterns
        only to be instantiated class IS31FL3197 
        '''
        def __init__(self, chip, scope):
            self._chip = chip
            self._scope = scope
            self.ADDR = self._chip.ADDR

        def config( self, 
                    start_time=0.0, 
                    rise_time=0.0, 
                    hold_time=0.0, 
                    fall_time=0.0, 
                    between_time=0.0, 
                    off_time=0.0, 
                    crossfade_time=0.0,
                    crossfade=False,
                    gamma='2.4',
                    cycles_1=1, 
                    cycles_2=1, 
                    cycles_3=1, 
                    multi_pulse_loops=1, 
                    pattern_loops=1, 
                    times16=False,
                    hold_time_selection='T4',
                    hold_time_function=False,
                    color_1=None, 
                    color_2=None, 
                    color_3=None,
                    activate=False
                    ):
            '''
            sends pattern config data to the chip 
            code in in order of register address, uses register names of documentation
            '''
            TS = self._check_time(start_time)
            T1 = self._check_time(rise_time)
            byte = (T1 << 4) | TS
            self._chip.i2c.writeto_mem(self.ADDR, 0x22, bytes([byte]))

            T2 = self._check_time(hold_time)
            T3 = self._check_time(fall_time)
            byte = (T3 << 4) | T2
            self._chip.i2c.writeto_mem(self.ADDR, 0x23, bytes([byte]))
            
            T4 = self._check_time(off_time)
            TP = self._check_time(between_time)
            byte = (TP << 4) | T4
            self._chip.i2c.writeto_mem(self.ADDR, 0x24, bytes([byte]))

            if crossfade:
                if color_1: C1 = crossfade # crossfade enable
                if color_2: C2 = crossfade
                if color_3: C3 = crossfade
            else:
                C1 = False # disable
                C2 = False
                C3 = False
            byte = (C3 << 2) | (C2 << 1) | C1
            self._chip.i2c.writeto_mem(self.ADDR, 0x25, bytes([byte]))

            TC = self._check_time(crossfade_time) # crossfade time
            byte = TC
            self._chip.i2c.writeto_mem(self.ADDR, 0x26, bytes([byte]))

            if color_1: CE1 = True # color enable
            else: CE1 = False 
            if color_2: CE2 = True
            else: CE2 = False 
            if color_3: CE3 = True
            else: CE3 = False
            byte = (CE3 << 2) | (CE2 << 1) | CE1
            self._chip.i2c.writeto_mem(self.ADDR, 0x27, bytes([byte]))

            CCT1 = self._check_cycles(cycles_1) # color loops
            CCT2 = self._check_cycles(cycles_2)
            CCT3 = self._check_cycles(cycles_3)
            byte = (CCT3 << 4) | (CCT2 << 2) | CCT1
            self._chip.i2c.writeto_mem(self.ADDR, 0x28, bytes([byte]))

            gammas = {'2.4':0b00, '3.5':0b01, 'linear':0b11} # gamma
            if gamma in gammas:
                GAM = gammas[gamma]
            else:
                raise ValueError (f'gamma {gamma} not allowed; use \'2.4\', \'3.5\' or \'linear\'')
            MTPLT = self._check_multi_pulse_loops(multi_pulse_loops) # multi pulse loops
            byte = (MTPLT << 4) | (GAM << 2)
            self._chip.i2c.writeto_mem(self.ADDR, 0x29, bytes([byte]))

            PLT_H = times16
            PLT_L = self._check_pattern_loops(pattern_loops) # pattern loops
            byte = (PLT_H << 7) | PLT_L
            self._chip.i2c.writeto_mem(self.ADDR, 0x2A, bytes([byte]))

            hold_times = {'T4':0b0, 'T2':0b1} # phase of pattern to stop in
            if hold_time_selection in hold_times:
                HT = hold_times[hold_time_selection]
            else:
                raise ValueError (f'hold_time_selection {hold_time_selection} not allowed; use T2 or T4')
            r = self._chip.i2c.readfrom_mem(self.ADDR, 0x06, 1)
            byte_value = r[0]
            byte_value &= 0b11111110 
            byte_value |= HT 
            self._chip.i2c.writeto_mem(self.ADDR, 0x06, bytes([byte_value]))

            CHF = hold_time_function # 
            r = self._chip.i2c.readfrom_mem(self.ADDR, 0x06, 1)
            byte_value = r[0]
            byte_value &= 0b11111101 
            byte_value |= CHF << 1
            self._chip.i2c.writeto_mem(self.ADDR, 0x06, bytes([byte_value]))

            if color_1: 
                self._chip._config_color_table(1, color_1)
            if color_2: 
                self._chip._config_color_table(2, color_2)
            if color_3: 
                self._chip._config_color_table(3, color_3)

            if activate:
                self.start()

        def start(self):
            '''
            activates pattern, requires prior call to config()
            '''
            self._chip._config_modus('pattern', 'rgb')
            self._chip.i2c.writeto_mem(self.ADDR, 0x2b, bytes([0xc5])) # color update register
            self._chip.i2c.writeto_mem(self.ADDR, 0x2d, bytes([0xc5])) # pattern times update register
        
        def stop(self):
            '''
            aborts pattern run by setting to modus pwmcl
            if no other actions inbetween, the pattern can be restarted with start()
            '''
            self._chip._config_modus('pwmcl', 'rgb')

        def clb(self, band):
            '''
            1..4
            '''
            self._chip._config_current_limit_band(band, 'rgb')

        def monitor(self, timeout): # [s]
            '''
            prints pattern execution status to the serial terminal for a time period
            use to familiarize with pattern generation behaviour and debugging only
            '''
            r_prev = None
            color_prev = None
            TS_prev = None
            start_time = time.ticks_ms()
            while True:
                # exit after timeout expired
                if time.ticks_diff(time.ticks_ms(), start_time) > timeout * 1000:
                    print('\ntimeout reached, exiting monitoring')
                    break
                # report status
                r = self._chip.i2c.readfrom_mem(self.ADDR, 0x0f, 1)
                if r != r_prev:
                    state = r[0]

                    color = None
                    if state & 0b00010000:
                        color = 1
                    if state & 0b00100000:
                        color = 2
                    if state & 0b01000000:
                        color = 3

                    if color and color != color_prev:
                        print(f'\nColor{color} ', end='')
                        color_prev = color

                    TS = state & 0b111
                    if TS != TS_prev:
                        print(f'TS{TS} ', end='')
                        TS_prev = TS

                    r_prev = r

        def _check_time(self, time):
            '''
            convenience function: maps any input between 0 and 10 (int or float) to the closest entry in the chip's table
            '''
            time_to_hex = {
                0.03: 0x0,
                0.13: 0x1,
                0.26: 0x2,
                0.38: 0x3,
                0.51: 0x4,
                0.77: 0x5,
                1.04: 0x6,
                1.60: 0x7,
                2.10: 0x8,
                2.60: 0x9,
                3.10: 0xa,
                4.20: 0xb,
                5.20: 0xc,
                6.20: 0xd,
                7.30: 0xe,
                8.30: 0xf,
            }            
            if 0.0 <= time <= 10:
                closest_time = min(time_to_hex.keys(), key=lambda t: abs(t - time))
                result = time_to_hex[closest_time]
            else:
                raise ValueError(f'time {time} not allowed; use 0 < time < 10 [s] - maps to closest time in table')
            return result

        def _check_cycles(self, value):
            if isinstance(value, int) and 1 <= value <= 3:
                result = value
            elif isinstance(value, str) and value == 'endless':
                result = 0
            else:
                raise ValueError(f'nr of cycles {value} not allowed; use 1..3 or \'endless\'')
            return result

        def _check_multi_pulse_loops(self, value):
            if isinstance(value, int) and 1 <= value <= 15:
                result = value
            elif isinstance(value, str) and value == 'endless':
                result = 0
            else:
                raise ValueError(f'nr of loops {value} not allowed; use 1..15 or \'endless\'')
            return result

        def _check_pattern_loops(self, value):
            if isinstance(value, int) and 1 <= value <= 64:
                result = value
            elif isinstance(value, str) and value == 'endless':
                result = 0
            else:
                raise ValueError(f'nr of loops {value} not allowed; use 1..64 or \'endless\'')
            return result

    '''
    interface to the chip
    '''
    def __init__(self, address):
        # Initialize I2C bus to get to the chip
        # for the arduino giga display shield, it's I2C4 on PB6 (SCL), PH12 (SDA)
        self.i2c = I2C(4) 
        devices = self.i2c.scan()
        self.ADDR = address 
        if self.ADDR not in devices:
            raise Exception('IS31FL3197 controller chip not found')

        self.reset()
        self.r = self._led(self, 'r')
        self.g = self._led(self, 'g')
        self.b = self._led(self, 'b')
        self.w = self._led(self, 'w') # not tested
        self.rgb = self._rgb(self, 'rgb')
        self.pattern = self._pattern(self, 'rgb')

    def reset(self):
        '''
        resets chip to known state
        '''
        self.i2c.writeto_mem(self.ADDR, 0x3f, bytes([0xc5])) # reset
        self.i2c.writeto_mem(self.ADDR, 0x01, bytes([0xf1])) # enable all outputs, sleep disable, normal operation 

    def _config_led(self, intensity, duty_cycle, band, scope):
        '''
        for individual leds
        '''
        self._config_modus('pwmcl', scope)
        self._config_intensity(intensity, scope)
        self._config_pwm(duty_cycle, scope)
        self._config_current_limit_band(band, scope)

    def _config_color(self, color, duty_cycle, band):
        '''
        for colors from tuple
        sets modus to pwmcl for all leds
        '''
        self._config_led(color[0], duty_cycle, band, 'r')        
        self._config_led(color[1], duty_cycle, band, 'g')        
        self._config_led(color[2], duty_cycle, band, 'b')  

    '''
    setting modus to 'pattern' is in pattern.start()
    '''

    def _config_intensity(self, intensity, scope):
        '''
        for individual leds or colors
        '''
        byte = int(intensity)
        if 0 <= byte <= 255:
            if 'r' in scope:
                self.i2c.writeto_mem(self.ADDR, 0x10, bytes([byte]))
            if 'g' in scope:
                self.i2c.writeto_mem(self.ADDR, 0x11, bytes([byte]))
            if 'b' in scope:
                self.i2c.writeto_mem(self.ADDR, 0x12, bytes([byte]))
            if 'w' in scope:
                self.i2c.writeto_mem(self.ADDR, 0x13, bytes([byte]))
            self.i2c.writeto_mem(self.ADDR, 0x2b, bytes([0xc5])) # color update register
        else:
            raise ValueError (f'intensity {intensity} not allowed; use 0..255')

    def _config_pwm(self, duty_cycle, scope):
        '''
        for individual leds or colors
        duty cycle ranges between 0..4095
        '''
        value = int(duty_cycle)
        if 0 <= value <= 4095:
            high_nibble = (value >> 8) & 0xFF
            low_byte = value & 0xFF
            if 'r' in scope:
                self.i2c.writeto_mem(self.ADDR, 0x1b, bytes([high_nibble]))
                self.i2c.writeto_mem(self.ADDR, 0x1a, bytes([low_byte]))
            if 'g' in scope:
                self.i2c.writeto_mem(self.ADDR, 0x1d, bytes([high_nibble]))
                self.i2c.writeto_mem(self.ADDR, 0x1c, bytes([low_byte]))
            if 'b' in scope:
                self.i2c.writeto_mem(self.ADDR, 0x1f, bytes([high_nibble]))
                self.i2c.writeto_mem(self.ADDR, 0x1e, bytes([low_byte]))
            if 'w' in scope:
                self.i2c.writeto_mem(self.ADDR, 0x21, bytes([high_nibble]))
                self.i2c.writeto_mem(self.ADDR, 0x20, bytes([low_byte]))
            self.i2c.writeto_mem(self.ADDR, 0x2c, bytes([0xc5])) # pwm update register        
        else:
            raise ValueError (f'duty cycle {duty_cycle} not allowed; use range 0..4095')

    def _config_modus(self, modus, scope):
        '''
        for individual leds or colors
        the chip allows each LED individually to be in any mode at anytime
        this driver assumes either led, color or pattern mode
        modus color and pattern preset modus for all leds, overwriting individual settings
        modus led presets modus for individual leds, 1 at a time
        so: AFTER setting color or pattern, 1 or 2 leds can be configured to operate independantly (not the other way round)
        '''
        r = self.i2c.readfrom_mem(self.ADDR, 0x02, 1)
        byte_value = r[0]

        if modus == 'pwmcl':
            if 'r' in scope:
                byte_value &= 0b11111100  # sets last two bits to '00'
            if 'g' in scope:
                byte_value &= 0b11110011
            if 'b' in scope:
                byte_value &= 0b11001111
            if 'w' in scope:
                byte_value &= 0b10111111 # not tested !
        elif modus == 'pattern':
            if 'r' in scope:
                byte_value &= 0b11111100 # clears last two bits
                byte_value |= 0b00000001 # sets last two bit to '01'
            if 'g' in scope:
                byte_value &= 0b11110011  
                byte_value |= 0b00000100 
            if 'b' in scope:
                byte_value &= 0b11001111  
                byte_value |= 0b00010000
            if 'w' in scope:
                raise ValueError (f'modus {modus} not allowed for \'w\'')
        elif modus == 'cl':
            if 'r' in scope:
                byte_value &= 0b11111100 # clears last two bits
                byte_value |= 0b00000011 # sets last two bits to '1x'
            if 'g' in scope:
                byte_value &= 0b11110011  
                byte_value |= 0b00001100 
            if 'b' in scope:
                byte_value &= 0b11001111  
                byte_value |= 0b00110000 
            if 'w' in scope:
                byte_value &= 0b10111111 # not tested !
                byte_value |= 0b01000000 
        else:
            raise ValueError (f'modus {modus} not allowed; use \'pwmcl\', \'pattern\' or \'cl\'')
        self.i2c.writeto_mem(self.ADDR, 0x02, bytes([byte_value]))

    def _config_current_limit_band(self, band, scope):
        '''
        for individual leds or colors
        puts a hard limit on the amount of current through each led
        uses 4 steps of 25% each
        '''
        bands = {1:0b00, 2:0b01, 3:0b10, 4:0b11}
        if band in bands:
            r = self.i2c.readfrom_mem(self.ADDR, 0x05, 1)
            byte_value = r[0]
            if 'r' in scope:
                byte_value &= 0b11111100
                byte_value |= bands[band] 
            if 'g' in scope:
                byte_value &= 0b11110011  
                byte_value |= bands[band] << 2
            if 'b' in scope:
                byte_value &= 0b11001111  
                byte_value |= bands[band] << 4
            if 'w' in scope:
                byte_value &= 0b00111111 # not tested !
                byte_value |= bands[band] << 6
            self.i2c.writeto_mem(self.ADDR, 0x05, bytes([byte_value]))
        else:
            raise ValueError (f'band {band} not allowed; use 1..4')
     
    def _config_color_table(self, table_nr, color):
        '''
        for patterns
        sets the r,g,b color codes based on a color-tuple
        '''
        if table_nr == 1:
            offset = 0
        elif table_nr == 2:
            offset = 4 # one byte extra for [on the Arduino Giga Shield the elusive] W led
        elif table_nr == 3:
            offset = 7
        else:
            raise ValueError (f'color table {id} not allowed; use 1..3')
        r  = int(color[0])
        g  = int(color[1])
        b  = int(color[2])
        self.i2c.writeto_mem(self.ADDR, 0x10+offset, bytes([r]))  # red
        self.i2c.writeto_mem(self.ADDR, 0x11+offset, bytes([g]))  # green
        self.i2c.writeto_mem(self.ADDR, 0x12+offset, bytes([b]))  # blue
        self.i2c.writeto_mem(self.ADDR, 0x2b, bytes([0xc5])) # color update register

    def _config_phase_delay(self, mode):
        '''
        sets output current phase delay
        the documentation does not clarify what that is
        so, this is just for completeness, untested and not enabled
        '''
        modes = {'mode1':0b0, 'mode2':0b1}
        if mode in modes:
            r = self.i2c.readfrom_mem(self.ADDR, 0x07, 1)
            byte_value = r[0]
            byte_value &= 0b11111110 
            byte_value |= modes[mode]
            self.i2c.writeto_mem(self.ADDR, 0x07, bytes([byte_value]))
        else:
            raise ValueError (f'mode {mode} not allowed; use \'mode1\' or \'mode2\'')
