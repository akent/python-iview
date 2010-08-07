import config
import comm
import os
import subprocess

def get_filename(url):
	return ''.join((
		'.'.join(url.split('.')[:-1]).split('/')[-1],
		'.flv',
	))

def rtmpdump(rtmp_url, rtmp_host, rtmp_app, rtmp_playpath, output_filename, resume=False, execvp=False):
	executables = (
			'rtmpdump',
			'rtmpdump_x86',
			'flvstreamer',
			'flvstreamer_x86',
		)

	args = [
			None, # Name of executable; written to later.
			'--host', rtmp_host,
			'--app',  rtmp_app,
			'--playpath', rtmp_playpath,
			'--swfhash',  config.swf_hash,
			'--swfsize',  config.swf_size,
			'--swfUrl',   config.swf_url,
		#	'-V', # verbose
			'-o', output_filename
		]

	if resume:
		args.append('--resume')

	if config.socks_proxy_host is not None:
		args.append('--socks')
		args.append(config.socks_proxy_host + ':' + str(config.socks_proxy_port))

	for exec_attempt in executables:
		print 'Starting %s...' % exec_attempt
		args[0] = exec_attempt
		try:
			if execvp:
				os.execvp(args[0], args)
			else:
				return subprocess.Popen(args, stderr=subprocess.PIPE)
		except OSError:
			print 'Could not load %s, trying another...' % exec_attempt
			continue

	print "It looks like you don't have a compatible downloader backend installed."
	print "See the README file for more information about setting this up properly."
	return False

def fetch_program(url, execvp=False, dest_file=None):
	if dest_file is None:
		dest_file = get_filename(url)

	if dest_file is not '-':
		resume = os.path.isfile(dest_file)
	else:
		resume = False

	auth = comm.get_auth()

	ext = url.split('.')[-1]
	url = '.'.join(url.split('.')[:-1]) # strip the extension (.flv or .mp4)

	url = auth['playpath_prefix'] + url

	if ext == 'mp4':
		url = ''.join(('mp4:', url))

	return rtmpdump(
			auth['rtmp_url'],
			auth['rtmp_host'],
			auth['rtmp_app'] + '?auth=' + auth['token'],
			url,
			dest_file,
			resume,
			execvp
		)
