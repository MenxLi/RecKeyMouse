import platform, os, subprocess

def openFile(filepath):
	"""Use system application to open a file"""
	# https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os
	if platform.system() == 'Darwin':       # macOS
		subprocess.call(('open', filepath))
	elif platform.system() == 'Windows':    # Windows
		os.startfile(filepath)
	else:                                   # linux variants
		subprocess.call(('xdg-open', filepath))