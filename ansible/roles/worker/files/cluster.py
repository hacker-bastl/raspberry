#!/usr/bin/env python

import datetime, psutil, random, re, socket, sys, time

import paho.mqtt.publish

if __name__ == '__main__' :
    hostname = None
    while not hostname :
        test = socket.socket()
        try :
            test.connect( ( '192.168.0.1', 80 ) )
            hostname = test.getsockname()[ 0 ]
        except :
            time.sleep( random.choice( [ 13, 19, 23, 29 ] ) )
    while True :
        processor, memory = int( psutil.cpu_percent() ), int( psutil.virtual_memory().percent )
        text = '%s cpu %s%% ram %s%%' % ( hostname, processor, memory )
        try :
            paho.mqtt.publish.single( 'raspberry/status', text, hostname = '192.168.0.10', port = 1883 )
        except :
            print >> sys.stderr, sys.exc_info()[ 1 ]
        time.sleep( random.choice( [ 13, 19, 23, 29 ] ) )
