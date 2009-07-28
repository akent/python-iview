import comm
from BeautifulSoup import BeautifulStoneSoup

def parse_config(soup):
	"""	There are lots of goodies in the config we get back from the ABC.
		In particular, it gives us the URLs of all the other XML data we
		need.
	"""

	xml = BeautifulStoneSoup(soup)

	return {
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
	rtmp_url = xml.find("server").string
	rtmp_chunks = rtmp_url.split('/')

	return {
		'rtmp_url'  : rtmp_url,
		'rtmp_host' : rtmp_chunks[2],
		'rtmp_app'  : rtmp_chunks[3],
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
		channels.append(channel['path'])

	return channels

def append_channel(soup, programme):
	xml = BeautifulStoneSoup(soup)

	listing = []

	for series in xml.findAll('series'):
		series_url = series.get('href')

		if series_url is None:
			continue

		# HACK: replace <abc: with < because BeautifulSoup doesn't have
		# any (obvious) way to inspect inside namespaces.
		series_soup = comm.maybe_fetch(series_url).replace('<abc:', '<').replace('</abc:', '</')
		series_xml = BeautifulStoneSoup(series_soup)

		for program in series_xml.findAll('item'):
			listing.append({
				'title' : program.find('title').string,
				'url'   : program.find('videoasset').string.split('.flv')[0]
				# we need to chop off the .flv off the end
				# as that's the way we need to give it to
				# the RTMP server for some reason
			})

	programme[xml.find('title').string] = listing

