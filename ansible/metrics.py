#!/usr/bin/env python

import prometheus_client, random, threading, time

print """ export sample metrics for prometheus
    https://github.com/prometheus/client_python/
    """

gauge = prometheus_client.Gauge( 'test_value', 'TEST of gauge' )

def process_request( value ) :
    gauge.set( value )
    time.sleep( random.random() )

def start_server( port = 9110 ) :
    prometheus_client.start_http_server( port )
    while True : process_request( 10 )

if __name__ == '__main__' :
    threading.Thread( target = start_server ).start()
