#!/usr/bin/env python

import BaseHTTPServer, random, subprocess, sys, threading, time


# https://docs.python.org/2/library/basehttpserver.html

class WebpageServer( BaseHTTPServer.HTTPServer ) :
    pass

class WebpageHandler( BaseHTTPServer.BaseHTTPRequestHandler ) :

    def send_command( self, command ) :
        path = '/home/pi/433Utils/RPi_utils/codesend'
        duration = 384
        protocol = 4
        valid = {
            'POST /bathroom' : 11926700,
            'POST /corridor' : 11719358,
            'POST /kitchen' : 11545397,
            'DELETE /bathroom' : 12406412,
            'DELETE /corridor' : 12372574,
            'DELETE /kitchen' : 11755989,
        }
        if not valid.has_key( command ) : return
        code = valid.get( command )
        command = '%s %s %s %s' % ( path, code, protocol, duration )
        subprocess.call( command, shell = True )

    def do_POST( self ) :
        self.send_response( 204 )
        self.end_headers()
        self.send_command( 'POST %s' % self.path )

    def do_DELETE( self ):
        self.send_response( 204 )
        self.end_headers()
        self.send_command( 'DELETE %s' % self.path )

    def do_GET( self ):
        self.send_response( 200 )
        self.send_header( 'Content-type', 'text/html' )
        self.end_headers()
        self.wfile.write( """<!doctype html>
<html lang="en">
  <head>
    <meta name="charset" value="utf-8">

    <title> Raspberry Controls </title>

    <script type="text/javascript">

        window.addEventListener('load', function() {
          var buttons = Array.prototype.slice.call(document.getElementsByTagName('input'));
          buttons.forEach(function(button) {
            var command = (button.getAttribute('name') || '');
            var address = command.split(/\ /g).slice(1).join(' ');
            var method = command.split(/\ /g).shift();
            button.addEventListener('click', function(event) {
              var request = new XMLHttpRequest();
              request.open(method, address);
              request.send(null);
              // event.returnValue = false;
              event.preventDefault();
              return false;
            });
          });
        });

    </script>
    <style type="text/css">

      body {
        font-family: sans-serif;
      }

      legend {
        font-weight: bold;
      }

      fieldset {
        margin: auto;
        width: 16em;
      }

    </style>
  </head>
  <body>
    <form action="javascript:void(0);">

      <fieldset>
        <legend>corridor</legend>
        <input name="POST /corridor" value="ON" type="button" />
        <input name="DELETE /corridor" value="OFF" type="button" />
      </fieldset>

      <fieldset>
        <legend>kitchen</legend>
        <input name="POST /kitchen" value="ON" type="button" />
        <input name="DELETE /kitchen" value="OFF" type="button" />
      </fieldset>

      <fieldset>
        <legend>bathroom</legend>
        <input name="POST /bathroom" value="ON" type="button" />
        <input name="DELETE /bathroom" value="OFF" type="button" />
      </fieldset>

    </form>
  </body>
</html>

""" )


if __name__ == '__main__' :
    while True :
        try : WebpageServer( ( '', 8000 ), WebpageHandler ).serve_forever()
        except : print >>sys.stderr, sys.exc_info()[ 1 ]
        time.sleep( random.choice( [ 13, 19, 23, 29 ] ) )
