from distutils.core import setup
import iview.config
setup(
	name='iview',
	version=iview.config.version,
	packages=['iview'],
	data_files=[
			('/usr/bin', ['iview-cli', 'iview-gtk']),
			('/usr/share/applications', ['iview-gtk.desktop']),
		],
	)
