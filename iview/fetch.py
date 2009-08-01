import comm
import os
import subprocess

def flvstreamer_x86(rtmp_host, rtmp_app, rtmp_playpath, output_filename, resume=False, execvp=False):
	args = [
			'flvstreamer_x86',
			'--host', rtmp_host,
			'--app',  rtmp_app,
			'--playpath', rtmp_playpath,
			'-o', output_filename
		]

	if resume:
		args.append('--resume')

	if execvp:
		os.execvp(args[0], args)
	else:
		return subprocess.Popen(args, stderr=subprocess.PIPE)

def fetch_program(url, execvp=False):
	filename = url.split('/')[1] + '.flv'
	resume = os.path.isfile(filename)

	return flvstreamer_x86(
			comm.auth['rtmp_host'],
			comm.auth['rtmp_app'] + '?auth=' + comm.auth['token'],
			url,
			filename,
			resume,
			execvp
		)
