import gtk
import comm
import config
from BeautifulSoup import BeautifulStoneSoup
try:
	import json
except ImportError:
	import simplejson as json

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
		'api_url' : xml.find('param', attrs={'name':'api'}).get('value'),
		'categories_url' : xml.find('param', attrs={'name':'categories'}).get('value'),
	}

def parse_auth(soup):
	"""	There are lots of goodies in the auth handshake we get back,
		but the only ones we are interested in are the RTMP URL, the auth
		token, and whether the connection is unmetered.
	"""

	xml = BeautifulStoneSoup(soup)

	# should look like "rtmp://203.18.195.10/ondemand"
	rtmp_url = xml.find('server').string

	playpath_prefix = ''

	if rtmp_url is not None:
		# Being directed to a custom streaming server (i.e. for unmetered services).
		# Currently this includes Hostworks for all unmetered ISPs except iiNet.

		rtmp_chunks = rtmp_url.split('/')
		rtmp_host = rtmp_chunks[2]
		rtmp_app = rtmp_chunks[3]
	else:
		# We are a bland generic ISP using Akamai, or we are iiNet.

		if not comm.iview_config:
			comm.get_config()

		playpath_prefix = config.akamai_playpath_prefix

		rtmp_url = comm.iview_config['rtmp_url']
		rtmp_host = comm.iview_config['rtmp_host']
		rtmp_app = comm.iview_config['rtmp_app']

	token = xml.find("token").string
	token = token.replace('&amp;', '&') # work around BeautifulSoup bug

	return {
		'rtmp_url'        : rtmp_url,
		'rtmp_host'       : rtmp_host,
		'rtmp_app'        : rtmp_app,
		'playpath_prefix' : playpath_prefix,
		'token'           : token,
		'free'            : (xml.find("free").string == "yes")
	}

def parse_index(soup, programme):
	"""	This function parses the index, which is an overall listing
		of all programs available in iView. The index is divided into
		'series' and 'items'. Series are things like 'beached az', while
		items are things like 'beached az Episode 8'.
	"""
	index = json.loads(soup)

	for series in index:
		series_iter = programme.append(None, [series['title'], series['id'], None, None])
		programme.append(series_iter, ['Loading...', None, None, None])

def parse_series_items(series_iter, soup, programme):
	# HACK: replace <abc: with < because BeautifulSoup doesn't have
	# any (obvious) way to inspect inside namespaces.
	soup = soup \
		.replace('<abc:', '<') \
		.replace('</abc:', '</')

	# HACK: replace &amp; with &#38; because HTML entities aren't
	# valid in plain XML, but the ABC doesn't know that.
	soup = soup.replace('&amp;', '&#38;')

	series_xml = BeautifulStoneSoup(soup)

	for program in series_xml.findAll('item'):
		programme.append(series_iter, [
				program.find('title').string,
				None,
				program.find('videoasset').string,
				program.find('description').string,
			])

