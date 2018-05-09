#!/usr/bin/env python

import colorsys, datetime, json, os, random, sys, threading, time, urllib, urllib2

import unicornhat ; unicornhat.clear()

unicornhat.set_layout( unicornhat.AUTO )

pixel_matrix = []

def display_metrics( values, warning = 0.7, intensity = 255 ) :
    pixel_matrix.append( values )
    while len( pixel_matrix ) >  4 : pixel_matrix.pop( 0 )
    for y, row in enumerate( pixel_matrix[ 0:4 ][ ::-1 ] ) :
        for x, percentage in enumerate( row[ 0:8 ] ) :
            brightness = percentage * ( 1.0 - y / 4.0 )
            if percentage > warning : red, green, blue = intensity * brightness, 0, 0
            else : red, green, blue = 0, intensity * brightness, 0
            hue, saturation, value = colorsys.rgb_to_hsv( red, green, blue )
            unicornhat.set_pixel_hsv( 8 - x - 1, y, hue, saturation, brightness )
            unicornhat.show()


def load_metrics( query, hostname = '192.168.0.10:9090' ) :
    response =  urllib2.urlopen( 'http://%s/api/v1/query?query=%s' % ( hostname, query ) ).read()
    metrics = dict( [ ( value.get( 'metric' ).get( 'instance' ).split( ':' ).pop( 0 ), value.get( 'value' ).pop() ) \
        for value in json.loads( response ).get( 'data' ).get( 'result' ) ] )
    if sys.stdin.isatty() : print json.dumps( metrics, indent = 4 )
    names = metrics.keys() ; names.sort()
    return [ float( metrics.get( instance ) ) for instance in names ]

def loop_query( query ) :
    while True :
        try : display_metrics( load_metrics( query ) )
        except : print >> sys.stderr, sys.exc_info()[ 1 ]
        wait = random.choice( [ 17, 23, 29 ] )
        time.sleep( wait )

if __name__ == '__main__' :
    loop_query( 'node_load1' )
