import json
from pathlib import PurePath
from os.path import relpath

#used by pyinstaller
def get_addfiles():

	dirname = PurePath(__file__).parent
	dir_relpath = PurePath(relpath(dirname))

	with open(dirname / 'templates.json') as f:
		temp = json.load(f)

	add_files = [
		(dirname / 'templates.json', dir_relpath),
		*((dirname / t_info['filename'], dir_relpath) for t_name, t_info in temp.items())
	]

	return add_files