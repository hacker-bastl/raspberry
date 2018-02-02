#!/usr/bin/env python

import blinkt, psutil, time

print """ display CPU status on a 8x1 LED Pimoroni "blinkt" board
    https://github.com/pimoroni/blinkt/blob/master/examples/
    http://docs.pimoroni.com/blinkt/
    """

while True :
    pixels = psutil.cpu_percent() / 100.0 * ( blinkt.NUM_PIXELS - 1 ) + 1
    red, green, blue, brightness = pixels < 5 and ( 0, 255, 0, 0.2 ) or ( 255, 0, 0, 1.0 )
    blinkt.set_brightness( brightness )
    for index in range( blinkt.NUM_PIXELS ) :
        if index > pixels : blinkt.set_pixel( index, 0, 0, 0 )
        else : blinkt.set_pixel( index, red, green, blue )
    blinkt.show()
    time.sleep( 1 )
