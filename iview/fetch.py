import config
import comm
import os
import subprocess

def flvstreamer(rtmp_url, rtmp_host, rtmp_app, rtmp_playpath, output_filename, resume=False, execvp=False):
	executables = (
			'rtmpdump',
			'rtmpdump_x86',
			'flvstreamer',
			'flvstreamer_x86',
		)

	args = [
			None, # Written to later
			'--host', rtmp_host,
			'--app',  rtmp_app,
			'--playpath', rtmp_playpath,
			'--swfhash',  config.swf_hash,
			'--swfsize',  config.swf_size,
			'--swfUrl',   config.swf_url,
			'--pageUrl',  config.page_url,
			'--tcUrl',    rtmp_url,
			'-V', # verbose
			'-o', output_filename
		]

	if resume:
		args.append('--resume')

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
		return

def fetch_program(url, execvp=False):
	filename = url.split('/')[-1] + '.flv'
	resume = os.path.isfile(filename)
	auth = comm.get_auth()

	return flvstreamer(
			auth['rtmp_url'],
			auth['rtmp_host'],
			auth['rtmp_app'] + '?auth=' + auth['token'],
			url,
			filename,
			resume,
			execvp
		)
