import machine, time
from machine import I2C
from IS31FL3197 import IS31FL3197

# some standard color schemes
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
WHITE    = (255, 255, 255)

is31 = IS31FL3197(80) # i2c address for the arduino giga display shield is 80 

# interface to the led
# below code is for red; same for is31.g and is31.b 
is31.r.on()             # fully on (intensity 255)
time.sleep(1) 
is31.r.intensity(64)   # 0..255
time.sleep(1)

is31.r.on()             
time.sleep(1)
is31.r.pwm(1023)        # 0..4095 
time.sleep(1) 

is31.r.on()
time.sleep(1) 
is31.r.clb(1)           # 1..4
time.sleep(1) 

is31.r.on()
time.sleep(1) 
is31.r.dim(50)          # 0..100%
time.sleep(1) 
is31.r.dim(50)          # sets to 50% of current 50%
time.sleep(1) 

is31.r.off();           # fully off
time.sleep(1) 

# interface to colors on all leds collectively
is31.rgb.color(RED)     # (0..255, 0..255, 0..255)
time.sleep(1)
is31.rgb.color(GREEN)
time.sleep(1)
is31.rgb.color(BLUE)
time.sleep(1)
is31.rgb.color(WHITE)
time.sleep(1)
is31.rgb.pwm(1023)      # 0..4095
time.sleep(1)
is31.rgb.off()
time.sleep(1)
is31.rgb.color(WHITE)
time.sleep(1)
is31.rgb.clb(1)         # 1..4
time.sleep(1)
is31.rgb.off()
time.sleep(1)

# interface to patterns
is31.pattern.config( 
                start_time=0.,               # in [s] anything betweeen 0-10s (maps to closest time in chip's table)
                rise_time=0., 
                hold_time=0., 
                fall_time=0., 
                between_time=0., 
                off_time=0., 
                crossfade_time=0.,
                crossfade=False,             # or False
                gamma='2.4',                # or '3.5' or 'linear' 
                cycles_1=1,                 # 1..3 or 'endless' (maps to 0)
                cycles_2=1, 
                cycles_3=1, 
                multi_pulse_loops=1,        # 1..15 or 'endless' (maps to 0)
                pattern_loops=64,           # 1..64 or 'endless' (maps to 0)
                times16=True,               # multiplies pattern_loops to maximum 64*16=1024
                hold_time_selection='T4',   # 'T4' or 'T2'
                hold_time_function=False,
                color_1=RED, 
                color_2=GREEN, 
                color_3=BLUE,
                activate = True
                )
time.sleep(5)

is31.pattern.config( 
                start_time=1,               # in [s] anything betweeen 0-10s (maps to closest time in chip's table)
                rise_time=1, 
                hold_time=1, 
                fall_time=1, 
                between_time=1, 
                off_time=1, 
                crossfade_time=1,
                crossfade=True,
                gamma='2.4',                # or '3.5' or 'linear' 
                cycles_1=1,                 # 1..3 or 'endless' (maps to 0)
                cycles_2=1, 
                cycles_3=1, 
                multi_pulse_loops=1,        # 1..15 or 'endless' (maps to 0)
                pattern_loops=64,           # 1..64 or 'endless' (maps to 0)
                times16=True,               # multiplies pattern_loops to maximum 64*16=1024
                hold_time_selection='T4',   # 'T4' or 'T2'
                hold_time_function=False,
                color_1=RED, 
                color_2=GREEN, 
                color_3=BLUE,
                activate = True
                )
print('entering sleep mode, notice pattern continues to run')
time.sleep(10)
print('woke up')
is31.pattern.stop()

is31.pattern.clb(1)                         # 1..4
is31.pattern.start()
is31.pattern.monitor(10)                    # period in [s]

print('notice pattern continues to run with green led continuous')
is31.g.on()
is31.g.dim(10)

time.sleep(10)
is31.pattern.stop() # green led stays on
print('pattern stopped, notice pattern green led stays on')
time.sleep(5)
is31.g.off()

print('done.')


