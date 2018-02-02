#!/usr/bin/env python

import HTMLParser, sys, time, urllib2

address = 'http://192.168.0.1/setup.cgi?next_file=stattbl.htm'

handler = urllib2.HTTPBasicAuthHandler()
handler.add_password( realm = 'NETGEAR DG834GB', uri = address, \
	user = 'admin', passwd = 'X0156048@mdsl.mnet-online.de' )
urllib2.install_opener( urllib2.build_opener( handler ) )

fields = { \
    61 : 'router_wan_packages_sent', \
    64 : 'router_wan_packages_received', \
    70 : 'router_wan_sent_per_second', \
    73 : 'router_wan_received_per_second', \
    76 : 'router_wan_uptime', \
    110 : 'router_wifi_packages_sent', \
    112 : 'router_wifi_packages_received', \
    116 : 'router_wifi_sent_per_second', \
    118 : 'router_wifi_received_per_second', \
    120 : 'router_wifi_uptime', \
    140 : 'router_dsl_down_speed', \
    142 : 'router_dsl_up_speed', \
    148 : 'router_dsl_down_loss', \
    150 : 'router_dsl_up_loss', \
    156 : 'router_dsl_down_noise', \
    158 : 'router_dsl_up_noise', \
}

class Status( object ) :
    def __init__( self, fields ) :
	self.fields, self.counter = fields, 0
        self.parser = HTMLParser.HTMLParser()
        self.parser.handle_data = self.parse
    def load( self, address ) :
        self.parser.feed( urllib2.urlopen( address ).read() )
	time.sleep( 3 )
    def parse( self, data ) :
	self.counter += 1
	if self.counter in self.fields :
	    print self.fields[ self.counter ], data

def check_status() :
    try : Status( fields ).load( address )
    except :
	   print >> sys.stderr, sys.exc_info()[ 1 ]
	   sys.exit( 1 )


check_status()
