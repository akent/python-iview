import os
import urllib
import gtk
import parser

config_url = 'http://www.abc.net.au/iview/iview_231_config.xml'
cache = False

auth = None
channels = None
programme = gtk.TreeStore(str, str)

def fetch_url(url):
	"""	Simple function that fetches a URL using URLlib.
	"""

	http = urllib.urlopen(url)

	if http.getcode() != 200:
		raise Exception(url)

	return http.read()

def maybe_fetch(url):
	"""	Only fetches a URL if it is not in the cache/ directory.
		In practice, this is really bad, and only useful for saving
		bandwidth when debugging. For one, it doesn't respect
		HTTP's wishes. Also, iView, by its very nature, changes daily.
	"""

	if not cache:
		return fetch_url(url)

	if not os.path.isdir('cache'):
		os.mkdir('cache')

	filename = os.path.join('cache', url.split('/').pop())

	if os.path.isfile(filename):
		f = open(filename, 'r')
		data = f.read()
		f.close()
	else:
		data = fetch_url(url)
		f = open(filename, 'w')
		f.write(data)
		f.flush()
		os.fsync(f.fileno())
		f.close()

	return data

def do_handshake():
	""" This function performs the initial handshake with iView.
		Among other things, it tells us if the connection is unmetered,
		and gives us a one-time token we need to use to speak RTSP with
		ABC's servers, and tells us what the RTMP URL is.
	"""
	global config, auth, channels

	config = parser.parse_config(maybe_fetch(config_url))
	auth = parser.parse_auth(maybe_fetch(config['auth_url']))
	channels = parser.parse_channels(maybe_fetch(config['channels_url']))

def get_programme(progress=None):
	"""	This function pulls the actual channel XML files, which contain
		pointers to the TV programs ('series'). The actual XML is parsed
		in the 'parser' module.
	"""

	global programme

	increment = 1.0 / len(channels)
	for channel in channels:
		if not progress is None:
			progress(increment, channel[0])
		try:
			channel_xml = maybe_fetch(channel[1])
			parser.append_channel(channel_xml, programme)
		except IOError:
			print 'Warning: unable to fetch', channel[1]
			pass

