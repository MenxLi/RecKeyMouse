import platform, os, subprocess
from typing import Union
import typing

def openFile(filepath):
	"""Use system application to open a file"""
	# https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os
	if platform.system() == 'Darwin':       # macOS
		subprocess.call(('open', filepath))
	elif platform.system() == 'Windows':    # Windows
		os.startfile(filepath)
	else:                                   # linux variants
		subprocess.call(('xdg-open', filepath))

def deleteDuplicate(lis, sort_key: Union[typing.Callable, None] = None):
	lis = list(set(lis))
	if not sort_key is None:
		lis.sort(key=sort_key)
	return lis