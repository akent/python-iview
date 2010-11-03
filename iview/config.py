import os

version     = '0.2'
api_version = 374

# os.uname() is not available on Windows, so we make this optional.
try:
	uname = os.uname()
	os_string = ' (%s %s %s)' % (uname[0], uname[2], uname[4])
except AttributeError:
	os_string = ' (non-Unix OS)'

user_agent = 'Python-iView %s%s' % (version, os_string)

config_url   = 'http://www.abc.net.au/iview/xml/config.xml?r=%d' % api_version
series_url   = 'http://www.abc.net.au/iview/api/series_mrss.htm?id=%s'
captions_url = 'http://www.abc.net.au/iview/captions/%s.xml'

akamai_playpath_prefix = '/flash/playback/_definst_/'

# Used for "SWF verification", a stream obfuscation technique
swf_hash    = '96cc76f1d5385fb5cda6e2ce5c73323a399043d0bb6c687edd807e5c73c42b37'
swf_size    = '2122'

swf_url     = 'http://www.abc.net.au/iview/images/iview.jpg'

# Used for decrypting the obfuscated index.xml file -- uses the RC4 cipher
index_password = 'wallace'

use_encryption = False

# Default configuration for SOCKS proxy.  If host is specified
# as 'None' then no proxy will be used.  The default port number
# will be used if only a host name is specified for the proxy.
socks_proxy_host = None
socks_proxy_port = 1080
