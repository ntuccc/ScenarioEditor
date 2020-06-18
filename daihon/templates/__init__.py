import json
from pathlib import PurePath

dirname = PurePath(__file__).parent

with open(dirname / 'templates.json') as f:
	temp = json.load(f)

#used by pyinstaller
add_files = [
	(dirname / 'templates.json', 'templates'),
	*((dirname / t_info['filename'], 'templates') for t_name, t_info in temp.items())
]