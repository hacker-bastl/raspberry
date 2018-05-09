#!/usr/bin/env python

import colorsys, math, random, time

# http://docs.pimoroni.com/pantilthat/

import pantilthat
pantilthat.light_mode( pantilthat.WS2812 )
pantilthat.light_type( pantilthat.GRBW )

pantilthat.pan( 0 )
pantilthat.tilt( 0 )
pantilthat.clear()
pantilthat.show()

while True :
    t = time.time()
    b = (math.sin(t * 2) + 1) / 2
    b = int(b * 255.0)
    t = round(time.time() * 1000) / 1000
    a = round(math.sin(t) * 90)
    pantilthat.pan(int(a))
    pantilthat.tilt(int(a))
    r, g, b = [int(x*255) for x in  colorsys.hsv_to_rgb(((t*100) % 360) / 360.0, 1.0, 1.0)]
    pantilthat.set_all(r, g, b)
    pantilthat.show()
    print(r, g, b, a)
    time.sleep(3)


def pan( value = -10 ) :
    target = pantilthat.get_pan() + value
    if target < 0.0 : target = 0.0
    pantilthat.pan( target )

def tilt( value = -10 ) :
    target = pantilthat.get_tilt() + value
    if target < 0.0 : target = 0.0
    pantilthat.tilt( target )




def light( red = 0, green = 0, blue = 0 ) :
    pixels = 8 * [ ( 0, 0, 0 ) ]
    pixels[ 1 ] = ( red, green, blue )
    pixels[ 6 ] = ( red, green, blue )
    pantilthat.clear()
    for index, color in enumerate( pixels ) :
        red, green, blue = color
        pantilthat.set_pixel( index, red, green, blue )
    pantilthat.show()


light( red = 32 )

pantilthat.pan( 0 )
pantilthat.tilt( 0 )
pantilthat.clear()
pantilthat.show()
