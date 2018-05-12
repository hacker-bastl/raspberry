#!/usr/bin/env python

import colorsys, json, random, sys, time, urllib, urllib2

import unicornhat
unicornhat.clear()
unicornhat.set_layout( unicornhat.AUTO )


def display_unicorn_pixels( values, warning = 0.7, intensity = 255 ) :
    for x, instance in enumerate( sorted( values.iterkeys() )[ 0:8 ][ ::-1 ] ) :
        for y, timestamp in enumerate( sorted( values.get( instance ).iterkeys() )[ 0:4 ][ ::-1 ] ) :
            percentage = float( values.get( instance ).get( timestamp ) )
            brightness = percentage * ( 1.0 - y / 4.0 )
            brightness *= random.choice( [ 0.9, 0.7, 0.5 ] ) # TODO
            if percentage > warning : red, green, blue = intensity * brightness, 0, 0
            else : red, green, blue = 0, intensity * brightness, 0
            hue, saturation, value = colorsys.rgb_to_hsv( red, green, blue )
            unicornhat.set_pixel_hsv( x, y, hue, saturation, brightness )
            unicornhat.show()


def load_prometheus_metrics( query, step = 60, count = 4, hostname = '192.168.0.10' ) :
    timestamp = int( time.time() ) ; start = timestamp - count * step
    query = [ ( 'query', query ), ( 'start', start ), ( 'end', timestamp ), ( 'step', step ) ]
    address = 'http://%s:9090/api/v1/query_range?%s' % ( hostname, urllib.urlencode( query ) )
    result = json.loads( urllib2.urlopen( address ).read() ).get( 'data' ).get( 'result' )
    metrics = dict( [ ( value.get( 'metric' ).get( 'instance' ).split( ':' ).pop( 0 ), \
        dict( value.get( 'values' ) ) ) for value in result ] )
    if sys.stdin.isatty() : print json.dumps( metrics, indent = 4 )
    return metrics


def loop_query( query ) :
    while True :
        try : display_unicorn_pixels( load_prometheus_metrics( query ) )
        except : print >> sys.stderr, sys.exc_info()[ 1 ]
        wait = random.choice( [ 17, 23, 29 ] )
        time.sleep( wait )


if __name__ == '__main__' :
    loop_query( 'node_load1' )
