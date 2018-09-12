#!/usr/bin/env python

import json, random, sys, time

import Adafruit_CharLCD
lcd = Adafruit_CharLCD.Adafruit_CharLCDPlate()
lcd.autoscroll( False )
lcd.show_cursor( True )
lcd.blink( True )


def format_message( message ) :
    return '%s\r\n%s' % ( str( message )[ 0:17 ], str( message )[ 18:35 ] )

def display_message( client, userdata, message ) :
    if type( message ) != type( '' ) :
        message = message.payload
    print >> sys.stdout, message
    lcd.clear()
    lcd.message( format_message( message ) )
    lcd.set_color( 0.0, 1.0, 0.0 )

def display_warning( message ) :
    print >> sys.stderr, message
    lcd.clear()
    lcd.message( format_message( message ) )
    lcd.set_color( 1.0, 0.0, 0.0 )

def subscribe_topic( client, userdata, flags, code ) :
    client.subscribe( 'raspberry/status' )
    display_message( None, None, 'connected' )


import paho.mqtt.client

def message_client( hostname, port = 1883 ) :
    client = paho.mqtt.client.Client()
    client.on_connect = subscribe_topic
    client.on_message = display_message
    client.connect( hostname, port )
    client.loop_forever()


if __name__ == '__main__' :
    display_warning( 'connecting' )
    while True :
        try : message_client( '192.168.0.10' )
        except : display_warning( sys.exc_info()[ 1 ] )
        time.sleep( random.choice( [ 29, 59, 61, 89 ] ) )
