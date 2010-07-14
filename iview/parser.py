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

		rtmp_url  = comm.iview_config['rtmp_url']
		rtmp_host = comm.iview_config['rtmp_host']
		rtmp_app  = comm.iview_config['rtmp_app']

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

def parse_index(soup):
	"""	This function parses the index, which is an overall listing
		of all programs available in iView. The index is divided into
		'series' and 'items'. Series are things like 'beached az', while
		items are things like 'beached az Episode 8'.
	"""
	index_json = json.loads(soup)
	index_json.sort(key=lambda series: series[1]) # alphabetically sort by title

	index_dict = []

	for series in index_json:
		# HACK: replace &amp; with & because HTML entities don't make
		# the slightest bit of sense inside a JSON structure.
		title = series[1].replace('&amp;', '&')

		index_dict.append({
			'id'    : series[0],
			'title' : title,
		})

	return index_dict

def parse_series_items(soup, get_meta=False):
	# HACK: replace <abc: and <media: with < because BeautifulSoup doesn't have
	# any (obvious) way to inspect inside namespaces.
	soup = soup \
		.replace('<abc:', '<')     \
		.replace('</abc:', '</')   \
		.replace('<media:', '<')   \
		.replace('</media:', '</') \

	# HACK: replace &amp; with & because HTML entities aren't
	# valid in plain XML, but the ABC doesn't know that.
	soup = soup.replace('&amp;', '&')

	series = BeautifulStoneSoup(soup)

	items = []

	for program in series.findAll('item'):
		items.append({
			'title'       : program.find('title').string,
			'url'         : program.find('videoasset').string,
			'description' : program.find('description').string,
			'thumb'       : program.find('thumbnail').get('url'),
			'date'        : program.find('transmitdate').string,
			'rating'      : program.find('rating').string,
			'link'        : program.find('player').get('url'), # link to play on iView site
			'home'        : program.find('linkurl').string, # program website
		})

	if get_meta:
		meta = {
			'title' : series.find('title').string,
			'link'  : series.find('link').string, # link to series listing on iView site
			'thumb' : series.find('image').find('url').string,
			'description' : series.find('description').string,
		}
		return (items, meta)
	else:
		return items
