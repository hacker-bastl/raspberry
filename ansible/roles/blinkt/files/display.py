#!/usr/bin/env python

import json, random, sys, time, urllib, urllib2

import blinkt
blinkt.clear()


def display_blinkt_pixels( metrics, warning = 0.7, intensity = 16 ) :
    values = [ float( metrics.get( instance ) ) for instance in sorted( metrics.iterkeys() ) ]
    for index, percentage in enumerate( values[ 0:8 ][ ::-1 ] ) :
        if percentage > warning : red, green, blue = intensity * percentage, 0, 0
        else : red, green, blue = 0, intensity * percentage, 0
        blinkt.set_pixel( index, red, green, blue, percentage )
    blinkt.show()


def load_prometheus_metrics( query, hostname = '192.168.0.10' ) :
    response =  urllib2.urlopen( 'http://%s:9090/api/v1/query?query=%s' % ( hostname, query ) ).read()
    metrics = dict( [ ( value.get( 'metric' ).get( 'instance' ).split( ':' ).pop( 0 ), value.get( 'value' ).pop() ) \
        for value in json.loads( response ).get( 'data' ).get( 'result' ) ] )
    if sys.stdin.isatty() : print json.dumps( metrics, indent = 4 )
    return metrics


def loop_query( query ) :
    while True :
        try : display_blinkt_pixels( load_prometheus_metrics( query ) )
        except : print >> sys.stderr, sys.exc_info()[ 1 ]
        wait = random.choice( [ 17, 23, 29 ] )
        time.sleep( wait )


if __name__ == '__main__' :
    loop_query( 'node_load1' )
