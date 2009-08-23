import comm
import os
import subprocess

def flvstreamer(rtmp_host, rtmp_app, rtmp_playpath, output_filename, resume=False, execvp=False):
	args = [
			'flvstreamer',
			'--host', rtmp_host,
			'--app',  rtmp_app,
			'--playpath', rtmp_playpath,
			'-o', output_filename
		]

	if resume:
		args.append('--resume')

	if execvp:
		try:
			os.execvp('flvstreamer_x86', args) # the upstream naming convention
		except OSError:
			os.execvp('flvstreamer', args)     # the Debian naming convention
	else:
		return subprocess.Popen(args, stderr=subprocess.PIPE)

def fetch_program(url, execvp=False):
	filename = url.split('/')[1] + '.flv'
	resume = os.path.isfile(filename)
	auth = comm.get_auth()

	return flvstreamer(
			auth['rtmp_host'],
			auth['rtmp_app'] + '?auth=' + auth['token'],
			url,
			filename,
			resume,
			execvp
		)
