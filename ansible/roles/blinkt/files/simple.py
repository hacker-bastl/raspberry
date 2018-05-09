#!/usr/bin/env python

import blinkt, psutil, time


def display( intensity = 0.5, threshold = 50, wait = 0.5 ) :
    pixels = 8 * [ 0.0, ]
    while True :
        load = max( [ psutil.cpu_percent(), psutil.virtual_memory().percent ] )
        pixels.append( load )
        pixels.pop( 0 )
        for index, percentage in enumerate( pixels ) :
            if percentage > threshold : red, green, blue = intensity * percentage, 0, 0
            else : red, green, blue = 0, intensity * percentage, 0
            blinkt.set_pixel( index, red, green, blue, percentage )
        blinkt.show()
        time.sleep( wait )


if __name__ == '__main__' :
    blinkt.clear()
    display( 0.1 )
