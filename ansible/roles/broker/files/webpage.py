#!/usr/bin/env python

import base64, hashlib, BaseHTTPServer, paho.mqtt.client, paho.mqtt.publish, SocketServer, sys, threading

# https://superuser.blog/websocket-server-python/

HTTP_101 = 'HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: %s\r\n\r\n'
HTTP_400 = 'HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n'

WEBSOCKET_HASH = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

# https://docs.python.org/2/library/socketserver.html#asynchronous-mixins

class WebsocketServer( SocketServer.ThreadingMixIn, SocketServer.TCPServer ) :
    pass

class WebsocketHandler( SocketServer.BaseRequestHandler ):

    def handle( self ) :
        headers = self.request.recv( 1024 ).strip().split( '\r\n' )
        valid = 'Connection: Upgrade' in headers and 'Upgrade: websocket' in headers
        if not valid : return self.request.sendall( HTTP_400 )
        request_key = str( ' ' ).join( [ header.split( ' ' ).pop() for header in headers if 'Sec-WebSocket-Key' in header ] )
        response_key = base64.standard_b64encode( hashlib.sha1( request_key + WEBSOCKET_HASH ).digest() )
        self.request.sendall( HTTP_101 % response_key )
        # def connect_mqtt_to_websocket( self ) :
        handler, connected = self, True
        def subscribe( client, userdata, flags, code ) :
            client.subscribe( 'raspberry/status' )
        def receive( client, userdata, message ) :
            try : handler.send_frame( message.payload )
            except: connected = False # TODO
        client = paho.mqtt.client.Client()
        client.on_connect = subscribe
        client.on_message = receive
        client.connect( '192.168.0.10', 1883 )
        while connected : client.loop_forever()

    def send_frame( self, payload ):
        frame = [ 129 ] + [ len( payload ) ]
        send  = bytearray( frame ) + payload
        self.request.sendall( send )


if __name__ == '__main__' :
    try :
        socketserver = WebsocketServer( ( '', 8080 ), WebsocketHandler )
        threading.Thread( target = socketserver.serve_forever ).start()
    except :
        print >>sys.stderr, sys.exc_info()[ 1 ]


# https://docs.python.org/2/library/basehttpserver.html

class WebpageServer( BaseHTTPServer.HTTPServer ) :
    pass

class WebpageHandler( BaseHTTPServer.BaseHTTPRequestHandler ) :
    def do_POST( self ) :
        self.send_response( 204 )
        self.end_headers()
        command = self.rfile.readline().strip()
        print str( command )
    def do_GET( self ):
        self.send_response( 200 )
        self.send_header( 'Content-type', 'text/html' )
        self.end_headers()
        self.wfile.write( HTML_PAGE )


HTML_PAGE = """<!DOCTYPE html>
<html>
    <head>
        <title> Raspberry Messages </title>
        <link type="image/png" href="//www.raspberrypi.org/app/themes/mind-control/images/favicon.png" rel="icon" />
        <script type="text/javascript">

            window.addEventListener( 'load', function restart() {
                var websocket = new WebSocket( 'ws://' + location.host.split( ':' ).shift() + ':8080' );
                websocket.onclose = function() { setTimeout( restart, 1E4 ); };
                websocket.onmessage = function( message ) {
                    console.log( message.data );
                    var node = document.createElement( 'li' );
                    var timestamp = new Date( new Date().getTime() - new Date()
                        .getTimezoneOffset() * 60 * 1E3 ).toJSON().substring( 11, 23 )
                    node.textContent = timestamp + ' ' + message.data;
                    var parent = document.querySelector( 'ul' );
                    if( parent.childNodes.length < 1 ) parent.appendChild( node );
                    else parent.insertBefore( node, parent.firstChild );
                    while( parent.childNodes.length > 32 ) parent.lastChild.remove()
                };
            } );

        </script>
        <style type="text/css">

            body {
                font-family: "Courier New", monospace;
                white-space: nowrap;
                overflow-x: hidden;
                overflow-y: scroll;
            }

            ul, li {
                list-style: none;
            }

        </style>
    </head>
    <body>
        <ul></ul>
    </body>
</html>

"""


if __name__ == '__main__' :
    try :
        webserver = WebpageServer( ( '', 8000 ), WebpageHandler )
        threading.Thread( target = webserver.serve_forever ).start()
    except :
        print >>sys.stderr, sys.exc_info()[ 1 ]
