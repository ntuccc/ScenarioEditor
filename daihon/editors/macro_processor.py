import re

class MacroBlock:
	def __init__(self, param = None):
		self.param = param
	def get_type(self):
		return self._type
	def get_param(self):
		return self.param

class _Plaintext(MacroBlock):
	_type = 'plaintext'
	param: str

class _None(MacroBlock):
	_type = 'none'

class _Separate(MacroBlock):
	_type = 'separate'
	param: list

class _Ruby(MacroBlock):
	_type = 'ruby'
	param: tuple

class Processor:
	macro = [
		{
			'class': _None,
			'keyword': 'none',
			'accept_args': [0]
		},
		{
			'class': _Separate,
			'keyword': 'separate',
			'accept_args': [0, 1]
		},
		{
			'class': _Ruby,
			'keyword': 'ruby',
			'accept_args': [2]
		}
	]
	def __init__(self, signal: str, split: str):
		signal = re.escape(signal)
		split = re.escape(split)
		self.sentence_regex = re.compile(fR'{signal}\s*(.*?)\s*{signal}')
		self.macro_regex = re.compile(split)
	def __call__(self, s: str):
		l = self.sentence_regex.split(s)
		result = []
		for i, text in enumerate(l):
			if i % 2 == 0:
				if text != '':
					result.append(_Plaintext(text))
			else:
				result.append(self.macro_process(text))
		if len(result) == 0:
			result.append(_Plaintext(''))
		return result
	def macro_process(s: str):
		l = self.macro_regex.split(s)
		keyword = l[0].lower() #case-insensitive

		args = l[1:]
		for m in macro:
			if m['keyword'] == keyword:
				if len(args) not in m['accept_args']:
					raise MacroError(f'{keyword} expects {m["accept_args"]} arguments, got {len(args)}.')
				return m['class'](args)
		raise MacroError(f'The macro "{keyword}" is not defined.')

class MacroError(ValueError):
	pass