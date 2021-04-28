#import re
from antlr4 import *
from .syntax.gscenarioLexer import gscenarioLexer
from .syntax.gscenarioParser import gscenarioParser

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
			'accept_args': [0],
			'recursive_args': []
		},
		{
			'class': _Separate,
			'keyword': 'separate',
			'accept_args': [0, 1],
			'recursive_args': [0]
		},
		{
			'class': _Ruby,
			'keyword': 'ruby',
			'accept_args': [2],
			'recursive_args': []
		}
	]
	class gscenarioVisitor(ParseTreeVisitor):
		# Visit a parse tree produced by gscenarioParser#text.
		def visitText(self, ctx:gscenarioParser.TextContext):
			n = ctx.getChildCount()
			result = [ctx.getChild(i).accept(self) for i in range(n)]
			return result

		# Visit a parse tree produced by gscenarioParser#text_in_macro.
		def visitText_in_macro(self, ctx:gscenarioParser.Text_in_macroContext):
			n = ctx.getChildCount()
			result = [ctx.getChild(i).accept(self) for i in range(n) if i % 2 == 0]
			#semantic part
			if len(result) < 1:
				raise MacroError(f'Empty Macro.')
			keyword = self._text_to_plaintext(result[0])
			if keyword is None:
				raise MacroError(f'The macro name should be a nonempty plaintext.')
			# strip
			# Deprecated: it is done by the processor
			#keyword = keyword.lstrip()
			#if len(result) == 1:
			#	keyword = keyword.rstrip()
			#elif type(result[-1]) is list and type(result[-1][-1]) is _Plaintext:
			#	result[-1][-1].param = result[-1][-1].param.rstrip()

			keyword = keyword.lower() #case-insensitive
			args = result[1:] # list of lists
			for m in Processor.macro:
				if m['keyword'] == keyword:
					if len(args) not in m['accept_args']:
						raise MacroError(f'{keyword} expects {m["accept_args"]} arguments, got {len(args)}.')
					# check all args and flatten if not recursive
					new_args = []
					for i, arg in enumerate(args):
						if i not in m['recursive_args']:
							# not recursive
							plaintext = self._text_to_plaintext(arg)
							if plaintext is None:
								raise MacroError(f'The No.{i} argument of "{ctx.getText()}" cannot be recursive.')
							# flatten
							new_args.append(plaintext)
						else:
							# recursive
							new_args.append(arg)
					return m['class'](new_args)
			raise MacroError(f'The macro "{keyword}" is not defined.')

		# Visit a parse tree produced by gscenarioParser#macro.
		def visitMacro(self, ctx:gscenarioParser.MacroContext):
			for i in range(ctx.getChildCount()):
				child = ctx.getChild(i)
				if isinstance(child, gscenarioParser.Text_in_macroContext):
					return self.visitText_in_macro(child)
			raise MacroError(f'Empty Macro.')

		# Visit a parse tree produced by gscenarioParser#plaintext.
		def visitPlaintext(self, ctx:gscenarioParser.PlaintextContext):
			return _Plaintext(ctx.getText())

		@staticmethod
		def _text_to_plaintext(text):
			if len(text) == 0:
				return ''
			if len(text) == 1:
				if type(text[0]) is _Plaintext:
					return text[0].param
			return None


	def __init__(self, signal: str, split: str):
		#signal = re.escape(signal)
		#split = re.escape(split)
		#self.sentence_regex = re.compile(fR'{signal}\s*(.*?)\s*{signal}')
		#self.macro_regex = re.compile(split)
		pass
	def __call__(self, s: str):
		text = InputStream(s)
		l = gscenarioLexer(text)
		stream = CommonTokenStream(l)
		parser = gscenarioParser(stream)
		tree = parser.text()
		visitor = self.gscenarioVisitor()
		return tree.accept(visitor)

class MacroError(ValueError):
	pass