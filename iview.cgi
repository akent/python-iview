#!/usr/bin/env python
"""	iView CGI script

	This is a script that you can place within your cgi-bin directory to allow
	you to download iView videos via HTTP. This is a fairly useless feature
	by itself, but very handy if you are trying to integrate iView with a
	system that needs to or prefers to download via HTTP.

	Usage:
		- place script in /usr/lib/cgi-bin or wherever your cgi-bin is
		- request a video via HTTP:
			$ wget http://localhost/cgi-bin/iview.cgi/730report_10_01_01.flv
		- enjoy!

	Note: if there is one thing going to go wrong with this script, it will be
	that it can't find the iview include module. Make sure that either the
	iview module is installed to the system (preferred), or the iview/
	directory is also under cgi-bin.

	Also, if there's the slightest chance somebody will be able to access this
	script from a public address, it's probably a good idea to configure
	your web server to restrict access to this script by IP address. Unless,
	of course, you want your web server acting as an iView proxy, chewing up
	bandwidth, violating copyright, getting your server taken down, etc.
"""

import os
import sys
import iview.comm
import iview.fetch

try:
	url = os.environ['PATH_INFO'].split('/')[-1].split(' ')[0]
except KeyError:
	url = None

# The above split(' ')[0] is called being paranoid about parameter injection.
# Yes, iview.fetch doesn't call the shell (it uses execvp()), but you never
# know how people are going to zombify this script. If iView ever starts using
# spaces, I'll update this script.

if url is None or len(url) <= 0:
	print 'Content-type: text/plain\r'
	print ''
	print """iView CGI script

To use this script, specify the video filename as a subdirectory of this script.
For example:
"""
	print 'http://' + os.environ['HTTP_HOST'] + os.environ['SCRIPT_NAME'] + '/730report_10_01_01.flv'
	sys.exit(0)

print 'Content-type: video/x-flv\r'
print '\r'

sys.stdout.flush() # If this isn't included, Apache doesn't see our headers and
                   # interprets rtmpdump output as HTTP headers.

iview.comm.get_config()
iview.fetch.fetch_program(url, execvp=True, dest_file='-')
