import os

version     = '0.2'
api_version = 320

# os.uname() is not available on Windows, so we make this optional.
try:
	uname = os.uname()
	os_string = ' (%s %s %s)' % (uname[0], uname[2], uname[4])
except AttributeError:
	os_string = ''

user_agent = 'Python-iView %s%s' % (version, os_string)

config_url = 'http://www.abc.net.au/iview/xml/config.xml?r=%d' % api_version
auth_url   = 'http://www2b.abc.net.au/iView/Services/iViewHandshaker.asmx/isp'
series_url = 'http://www.abc.net.au/iview/api/series.htm?id=%s'

akamai_playpath_prefix = 'flash/playback/_definst_/'

# Used for "SWF verification", a stream obfuscation technique
swf_hash    = 'a3eddcc12a96169882f99522a0835e629ae544f2f0bbeb1de4a6ed72754ac965'
swf_size    = '1774'

swf_url     = 'http://www.abc.net.au/iview/netConnectionWrapper.swf'
page_url    = 'http://www.abc.net.au/iview/'

# Used for decrypting the obfuscated index.xml file -- uses the RC4 cipher
index_password = 'wallace'

use_encryption = False
