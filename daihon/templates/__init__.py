import json
from pathlib import PurePath
from os.path import relpath

#used by pyinstaller
def get_addfiles(project_path = None):

	dirname = PurePath(__file__).parent
	if project_path is None:
		dir_relpath = PurePath(relpath(dirname))
	else:
		dir_relpath = PurePath(relpath(dirname, project_path))

	with open(dirname / 'templates.json') as f:
		temp = json.load(f)

	add_files = [
		(dirname / 'templates.json', dir_relpath),
		*((dirname / t_info['filename'], dir_relpath) for t_name, t_info in temp.items())
	]

	return add_files