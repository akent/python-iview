import comm, fetch
from comm import do_handshake, get_programme

def version():
	return "0.1"

def __init__():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'c', ['cache'])
	except getopt.GetoptError, err:
		pass

	for o in opts:
		if o in ('-c', '--cache'):
			comm.cache = True
