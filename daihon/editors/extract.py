import json
from pathlib import Path
from importlib.resources import open_text, path as resource_path

from .macro_processor import Processor
from .filters import filters
from .. import templates

class Extractor:
	def __init__(self):
		with open_text(templates, 'templates.json') as file:
			#After Py 3.7 dict preserves the order
			self.templates = json.load(file)
	def extract(self, tname, scenario, filename):
		if tname not in self.templates:
			return
		getattr(self, f'_extract_with_{self.templates[tname]["renderer"]}')(tname, scenario, filename)
	def _extract_with_jinja2(self, tname, scenario, filename):
		from jinja2 import Environment, FileSystemLoader
		from jinja2.ext import i18n, do, loopcontrols, with_
		info = self.templates[tname]
		print(info)
		if not hasattr(self, f'_extract_env_{tname}'):
			with resource_path(templates, '.') as path:
				e = Environment(loader = FileSystemLoader(str(path)), extensions = [i18n, do, loopcontrols, with_], **info['env_param'])
				for n, f in filters.items():
					e.filters[n] = f
				setattr(self, f'_extract_env_{tname}', e)
		template = getattr(self, f'_extract_env_{tname}').get_template(info['filename'])
		with open(f'{Path(filename).stem}.{info["suffix"]}', 'w', encoding = 'utf-8') as file:
			file.write(template.render({'scenario': scenario, 'MacroProcessor': Processor}))
	def _extract_with_docxtpl(self, tname, scenario, filename):
		from jinja2 import Environment
		from jinja2.ext import i18n, do, loopcontrols, with_
		from docxtpl import DocxTemplate
		info = self.templates[tname]
		if not hasattr(self, f'_extract_env_{tname}'):
			e = Environment(extensions = [i18n, do, loopcontrols, with_], **info['env_param'])
			for n, f in filters.items():
				e.filters[n] = f
			setattr(self, f'_extract_env_{tname}', e)
		with resource_path(templates, info['filename']) as template_path:
			doctemplate = DocxTemplate(str(template_path))
		doctemplate.render({'scenario': scenario}, getattr(self, f'_extract_env_{tname}'))
		doctemplate.save(f'{Path(filename).stem}.{info["suffix"]}')