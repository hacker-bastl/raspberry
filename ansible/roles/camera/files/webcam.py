#!/usr/bin/env python3

import io, logging, picamera, socketserver, sys, threading, time

# https://www.raspberrypi.org/forums/viewtopic.php?t=196337

from http import server

HTML_PAGE = """<!DOCTYPE html>
<html>
    <head>
        <title> Raspberry Webcam </title>
        <link type="image/png" href="//www.raspberrypi.org/app/themes/mind-control/images/favicon.png" rel="icon" />
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
                    request.open( 'POST', '//' + location.host );
                    request.send( event.key );
                }
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


class StreamingHandler( server.BaseHTTPRequestHandler ):
    def do_GET( self ) :
        if self.path in ( '', '/', '/index.htm', '/index.html' ) :
            content = HTML_PAGE.encode( 'utf-8' )
            self.send_response( 200 )
            self.send_header( 'Content-Type', 'text/html' )
            self.send_header( 'Content-Length', len( content ) )
            self.end_headers()
            self.wfile.write( content )
        elif self.path in( '/camera.mjpg', '/stream.mjpg' ) :
            self.send_response( 200 )
            self.send_header( 'Age', 0 )
            self.send_header( 'Cache-Control', 'no-cache, private' )
            self.send_header( 'Pragma', 'no-cache' )
            self.send_header( 'Content-Type', 'multipart/x-mixed-replace; boundary=FRAME' )
            self.end_headers()
            try :
                while True :
                    with output.condition :
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write( b'--FRAME\r\n' )
                    self.send_header( 'Content-Length', len( frame ) )
                    self.send_header( 'Content-Type', 'image/jpeg' )
                    self.end_headers()
                    self.wfile.write( frame )
                    self.wfile.write( b'\r\n' )
            except Exception as error :
                logging.warning( 'disconnected %s: %s', self.client_address, str( error ) )
        else :
            self.send_error( 404 )
            self.end_headers()
    def do_POST( self ) :
        command = self.rfile.readline().strip()
        self.send_response( 204 )
        self.end_headers()
        # TODO
        logging.warning( str( command ) )


class StreamingServer( socketserver.ThreadingMixIn, server.HTTPServer ):
    allow_reuse_address = True
    daemon_threads = True


with picamera.PiCamera( resolution = ( 1280, 720 ), framerate = 25 ) as camera:
    camera.rotation = 180
    camera.led = True
    output = StreamingOutput()
    camera.start_recording( output, format = 'mjpeg' )
    time.sleep( 13 )
    try:
        server = StreamingServer( ( '', 8000 ), StreamingHandler )
        server.serve_forever()
    except :
        print >>sys.stderr, sys.exc_info()[ 1 ]
    finally:
        camera.stop_recording()
