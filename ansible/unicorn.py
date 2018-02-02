#!/usr/bin/env python

print """ check if our infrastructure is online (via "curl" to public test route)
    visualize current and recent platform status with bars on "matrtix" Raspberry LEDs
    https://intranet.allianz.com.awin/communities/groups/digital-lab/blog/2018/01/
    http://url.allianz/raspberry
    """

import colorsys, random, unicornhat


print """ display status on a 8x4 LED Pimoroni "unicorn-hat" board
    https://shop.pimoroni.com/products/unicorn-phat/
    https://github.com/pimoroni/unicorn-hat/
    http://docs.pimoroni.com/unicornhat/
    """

class StatusDisplay( object ) :
    def __init__( self, width, height ) :
        self.buffer = [ [ ( 0, 0, 0, 0 ) for y in range( height ) ] for x in range( width ) ]
        unicornhat.clear()
    def show( self ) :
        for counter, column in enumerate( self.buffer ) :
            for y, cell in enumerate( column ) :
                red, green, blue, brightness = cell
                hue, saturation, value = colorsys.rgb_to_hsv( red, green, blue )
                x = y % 2 < 1 and counter or len( self.buffer ) - 1 - counter
                unicornhat.set_pixel_hsv( y, x, hue, saturation, brightness )
                deduct = brightness > 0.8 and 0.1 or random.choice( [ 0.1, 0.2 ] )
                if brightness > deduct : update = brightness - deduct
                else : red, green, blue, update = 0, 0, 0, 0
                column[ y ] = red, green, blue, update
        unicornhat.show()
    def color( self, value ) :
        if value == StatusDisplay.GOOD : return [ ( 0, 255, 0, b ) for b in ( 0.6, 1.0, 0.6, 0.4 ) ]
        elif value == StatusDisplay.MEDIUM : return [ ( 0, 255, 0, b ) for b in ( 0.4, 1.0, 0.4, 0.0 ) ]
        elif value == StatusDisplay.BAD : return [ ( 0, 255, 0, b ) for b in ( 0.2, 1.0, 0.2, 0.0 ) ]
        else : return [ ( 255, 0, 0, b ) for b in ( 0.6, 1.0, 0.6, 0.0 ) ]
    def update( self, value = 0 ) :
        self.buffer.append( self.color( value ) )
        self.buffer.pop( 0 )
        self.show()


StatusDisplay.GOOD, StatusDisplay.MEDIUM, StatusDisplay.BAD, StatusDisplay.ERROR = 3, 2, 1, 0


import paho.mqtt.client, paho.mqtt.publish, sys, time

class MessageClient( object ) :
    def __init__( self, topic = 'bastl/raspberry',  hostname = 'iot.eclipse.org', port = 1883 ) :
        self.topic, self.hostname, self.port, self.active = topic, hostname, port, True
    def publish( self, message ) :
        try : paho.mqtt.publish.single( self.topic, message, hostname = self.hostname, port = self.port )
        except Exception : self.fail( 'publish failed')
    def subscribe( self, client, userdata, flags, code ) :
        client.subscribe( self.topic )
    def receive( self, client, userdata, message ) :
        try : self.display( int( message.payload ) )
        except : return self.fail( 'invalid message' )
    def connect( self, timeout ) :
        client = paho.mqtt.client.Client()
        client.on_connect = self.subscribe
        client.on_message = self.receive
        client.connect( self.hostname, self.port, timeout )
        client.loop_forever()
    def fail( self, message ) :
        self.display( StatusDisplay.ERROR )
        print >> sys.stderr, message
    def display( self, value ) :
        raise Exception( 'not implemented' )
    def run( self, timeout = 7 ) :
        while True :
            try : self.connect( timeout )
            except Exception : self.fail( 'connect failed' )
            time.sleep( timeout )


import threading, shlex, socket, subprocess, tempfile

client = MessageClient()
client.display = StatusDisplay( 8, 4 ).update
threading.Thread( target = client.run ).start()
while True :
    time.sleep( random.choice( [ 2, 6, 8 ] ) )
    client.publish( random.choice( [ StatusDisplay.GOOD, StatusDisplay.MEDIUM, StatusDisplay.BAD, StatusDisplay.ERROR ] ) )

    # TODO

    """

    url = '%s:%s@%s/%s.git' % ( GHE_USER, GHE_TOKEN, GHE_HOST, GHE_REPO )
    command = 'git clone --depth 1 https://%s' % url
    workdir = tempfile.mkdtemp()
    success = 0 == subprocess.check_call( command, \
        shell = True, cwd = workdir, stderr = subprocess.PIPE )
    subprocess.call( shlex.split('rm -rf "%s"' % workdir )  )

    """
