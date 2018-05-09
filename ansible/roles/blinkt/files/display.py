#!/usr/bin/env python

import colorsys, datetime, json, os, random, sys, threading, time, urllib, urllib2

import blinkt ; blinkt.clear()

def display_metrics( values, warning = 0.7, intensity = 16 ) :
    for pixel, percentage in enumerate( values[ 0:8 ] ) :
        if percentage > warning : red, green, blue = intensity * percentage, 0, 0
        else : red, green, blue = 0, intensity * percentage, 0
        index = blinkt.NUM_PIXELS - pixel - 1
        blinkt.set_pixel( index, red, green, blue, percentage )
    blinkt.show()


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
