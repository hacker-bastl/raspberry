#!/usr/bin/env python

import SimpleHTTPServer, SocketServer, os


class Handler( SimpleHTTPServer.SimpleHTTPRequestHandler ) :
    pass


if __name__ == '__main__' :
    os.chdir( '/var/www/' )
    server = SocketServer.TCPServer( ( '', 80 ), Handler )
    server.serve_forever()
