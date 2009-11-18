import gtk
import comm
from BeautifulSoup import BeautifulStoneSoup

def parse_config(soup):
	"""	There are lots of goodies in the config we get back from the ABC.
		In particular, it gives us the URLs of all the other XML data we
		need.
	"""

	soup = soup.replace('&amp;', '&#38;')

	xml = BeautifulStoneSoup(soup)

	# should look like "rtmp://cp53909.edgefcs.net/ondemand"
	rtmp_url = xml.find('param', attrs={'name':'server_streaming'}).get('value')
	rtmp_chunks = rtmp_url.split('/')

	return {
		'rtmp_url'  : rtmp_url,
		'rtmp_host' : rtmp_chunks[2],
		'rtmp_app'  : rtmp_chunks[3],
		'auth_url' : xml.find('param', attrs={'name':'auth_path'}).get('value'),
		'channels_url' : 
			xml.find('param', attrs={'name':'base_url'}).get('value')
			+ '/'
			+ xml.find('param', attrs={'name':'xml_channels'}).get('value')
	}

def parse_auth(soup):
	"""	There are lots of goodies in the auth handshake we get back,
		but the only ones we are interested in are the RTMP URL, the auth
		token, and whether the connection is unmetered.
	"""

	xml = BeautifulStoneSoup(soup)

	# should look like "rtmp://203.18.195.10/ondemand"
	rtmp_url = xml.find('server').string

	if rtmp_url is not None:
		# the ISP provides their own iView server, i.e. unmetered
		rtmp_chunks = rtmp_url.split('/')
		rtmp_host = rtmp_chunks[2]
		rtmp_app = rtmp_chunks[3]
	else:
		# we are a bland generic ISP
		rtmp_url = comm.config['rtmp_url']
		rtmp_host = comm.config['rtmp_host']
		rtmp_app = comm.config['rtmp_app']

	return {
		'rtmp_url'  : rtmp_url,
		'rtmp_host' : rtmp_host,
		'rtmp_app'  : rtmp_app,
		'token'     : xml.find("token").string,
		'free'      : (xml.find("free").string == "yes")
	}

def parse_channels(soup):
	"""	This function will grab the channels list, to be parsed
		and fetched separately. Returns an array of URLs.
	"""
	xml = BeautifulStoneSoup(soup)

	channels = []

	all_channels = xml.findAll("channel")

	for channel in all_channels:
		channels.append([channel.find('name').string, channel['path']])

	return channels

def append_channel(soup, programme):
	xml = BeautifulStoneSoup(soup)

	gtk.gdk.threads_enter()
	channel_iter = programme.append(None, [xml.find('title').string, None, xml.find('description').string])
	gtk.gdk.threads_leave()

	for series in xml.findAll('series'):
		series_url = series.get('href')

		if series_url is None:
			continue

		try:
			# HACK: replace <abc: with < because BeautifulSoup doesn't have
			# any (obvious) way to inspect inside namespaces.
			series_soup = comm.maybe_fetch(series_url) \
				.replace('<abc:', '<') \
				.replace('</abc:', '</')

			# HACK: replace &amp; with &#38; because HTML entities aren't
			# valid in plain XML, but the ABC doesn't know that.
			series_soup = series_soup.replace('&amp;', '&#38;')

			series_xml = BeautifulStoneSoup(series_soup)
		except IOError:
			print 'Warning: unable to fetch', series_url
			pass

		gtk.gdk.threads_enter()
		for program in series_xml.findAll('item'):
			programme.append(channel_iter, [
					program.find('title').string,
					program.find('videoasset').string.split('.flv')[0],
					# we need to chop off the .flv off the end
					# as that's the way we need to give it to
					# the RTMP server for some reason
					program.find('description').string,
				])
		gtk.gdk.threads_leave()

