#!/usr/bin/env python3

import colorsys, io, logging, math, pantilthat, picamera, random, socketserver, sys, threading, time


from http import server

# http://docs.pimoroni.com/pantilthat/

if __name__ == '__main__' :
    pantilthat.light_mode( pantilthat.WS2812 )
    pantilthat.light_type( pantilthat.GRBW )
    pantilthat.pan( 0 )
    pantilthat.tilt( 0 )
    pantilthat.clear()
    pantilthat.show()


HTML_PAGE = """<!doctype html>
<html lang="en">
    <head>
        <meta name="charset" value="utf-8">

        <title> Raspberry Webcam </title>

        <style type="text/css">

            html, body, img {
                background-color: #000;
                cursor: progress;
                width: 100%;
                height: 100%;
                overflow: hidden;
                padding: 0px;
                margin: 0px;
            }

        </style>
        <script type="text/javascript">

            window.addEventListener( 'keyup', function( event ) {
              var valid = [ 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', '+', '-' ];
              if( valid.indexOf( event.key ) > -1 ) {
                  var request = new XMLHttpRequest();
                  request.open( 'POST', '//' + location.host + '/' + event.key );
                  request.send( null );
              }
            } );

        </script>
        <script type="text/javascript">

            window.addEventListener( 'load', function restart() {
                var websocket = new WebSocket( 'ws://192.168.0.10:8000' );
                websocket.onclose = function() { setTimeout( restart, 1E4 ); };
                websocket.onmessage = function( message ) {
                  console.log( message.data );
                };
            } );

        </script>
    </head>
    <body>
        <img src="stream.mjpg" />
    </body>
</html>

"""


class StreamingOutput( object ) :
    def __init__( self ) :
        self.condition = threading.Condition()
        self.buffer = io.BytesIO()
        self.frame = None
    def write( self, buffer ) :
        if buffer.startswith( b'\xff\xd8' ) :
            self.buffer.truncate()
            with self.condition :
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek( 0 )
        return self.buffer.write( buffer )


class StreamingServer( socketserver.ThreadingMixIn, server.HTTPServer ):
    allow_reuse_address = True
    daemon_threads = True


# https://www.raspberrypi.org/forums/viewtopic.php?t=196337

class WebcamHandler( server.BaseHTTPRequestHandler ):

    def do_GET( self ) :
        if self.path in( '/camera.mjpg', '/stream.mjpg' ) :
            self.send_response( 200 )
            self.send_header( 'Age', 0 )
            self.send_header( 'Cache-Control', 'no-cache, private' )
            self.send_header( 'Pragma', 'no-cache' )
            self.send_header( 'Content-Type', 'multipart/x-mixed-replace; boundary=WEBCAMFRAME' )
            self.end_headers()
            while True :
                with output.condition :
                    output.condition.wait()
                    frame = output.frame
                try :
                    self.wfile.write( b'--WEBCAMFRAME\r\n' )
                    self.send_header( 'Content-Length', len( frame ) )
                    self.send_header( 'Content-Type', 'image/jpeg' )
                    self.end_headers()
                    self.wfile.write( frame )
                    self.wfile.write( b'\r\n' )
                except Exception as error :
                    logging.warning( 'disconnected %s: %s', self.client_address, str( error ) )
                    print( error )
                    break
        elif self.path in ( '', '/', '/index.htm', '/index.html' ) :
            content = HTML_PAGE.encode( 'utf-8' )
            self.send_response( 200 )
            self.send_header( 'Content-Type', 'text/html' )
            self.send_header( 'Content-Length', len( content ) )
            self.end_headers()
            self.wfile.write( content )
        else :
            self.send_error( 404 )
            self.end_headers()

    def do_POST( self ) :
        self.send_response( 204 )
        self.end_headers()
        if self.path == '/ArrowUp' :
            return self.do_PAN( - 7 )
        if self.path == '/ArrowDown' :
            return self.do_PAN( 7 )
        if self.path == '/ArrowLeft' :
            return self.do_TILT( 7 )
        if self.path == '/ArrowRight' :
            return self.do_TILT( - 7 )
        if self.path == '/+' :
            return self.do_LIGHT( 255 )
        if self.path == '/-' :
            return self.do_LIGHT( 64 )
        print( str( self.path ) )

    def do_PAN( self, value = 0, maximum = 70 ) :
        target = pantilthat.get_pan() + value
        if target < - maximum  : target = - maximum
        if target > maximum  : target = maximum
        print( value, target )
        pantilthat.pan( target )

    def do_TILT( self, value = 0, maximum = 70 ) :
        target = pantilthat.get_tilt() + value
        if target < - maximum  : target = - maximum
        if target > maximum  : target = maximum
        print( value, target )
        pantilthat.tilt( target )

    def do_LIGHT( self, value = 0 ) :
        if value < 0 : value = 0
        if value > 255 : value = 255
        pantilthat.clear()
        pantilthat.set_all( value, value, value )
        pantilthat.show()


if __name__ == '__main__' :
    time.sleep( 7 )

    with picamera.PiCamera( resolution = ( 1024, 768 ), framerate = 25 ) as camera:
        camera.rotation = 180
        camera.led = True
        output = StreamingOutput()
        camera.start_recording( output, format = 'mjpeg' )
        try : StreamingServer( ( '', 8000 ), WebcamHandler ).serve_forever()
        except : print >>sys.stderr, sys.exc_info()[ 1 ]
        finally: camera.stop_recording()
