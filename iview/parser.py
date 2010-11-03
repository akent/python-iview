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
		'auth_url'  : xml.find('param', attrs={'name':'auth'}).get('value'),
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
	index_json.sort(key=lambda series: series['b']) # alphabetically sort by title

	index_dict = []

	for series in index_json:
		# HACK: replace &amp; with & because HTML entities don't make
		# the slightest bit of sense inside a JSON structure.
		title = series['b'].replace('&amp;', '&')

		index_dict.append({
			'id'    : series['a'],
			'title' : title,
		})

	return index_dict

def parse_series_items(soup, get_meta=False):
	series_json = json.loads(soup)

	items = []

	for item in series_json[0]['f']:
		for optional_key in ('d', 'r', 's', 'l'):
			try:
				item[optional_key]
			except KeyError:
				item[optional_key] = ''

		try:
			items.append({
				'id'          : item['a'],
				'title'       : item['b'].replace('&amp;', '&'), # HACK. See comment in parse_index()
				'description' : item['d'].replace('&amp;', '&'),
				'url'         : item['n'],
				'livestream'  : item['r'],
				'thumb'       : item['s'],
				'date'        : item['f'],
				'home'        : item['l'], # program website
			})
		except KeyError:
			print 'An item we parsed had some missing info, so we skipped an episode. Maybe the ABC changed their API recently?'

	if get_meta:
		meta = {
			'id'    : series_json['a'],
			'title' : series_json['b'],
			'thumb' : series_json['d'],
		}
		return (items, meta)
	else:
		return items

def parse_captions(soup):
	"""	Converts custom iView captions into SRT format, usable in most
		decent media players.
	"""
	xml = BeautifulStoneSoup(soup)

	output = u''

	i = 1
	for title in xml.findAll('title'):
		start = title['start']
		ids = start.rfind(':')
		end = title['end']
		ide = end.rfind(':')
		output = output + str(i) + u'\n'
		output = output + start[:ids] + u',' + start[ids+1:] + u' --> ' + end[:ide] + ',' + end[ide+1:] + u'\n'
		output = output + title.string.replace('|','\n') + u'\n\n'
		i += 1

	return output
