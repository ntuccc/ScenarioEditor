from __future__ import annotations
from collections import defaultdict
from io import IOBase
from itertools import takewhile, dropwhile
from typing import Optional, Dict, Tuple, Callable, Mapping, MutableMapping
from warnings import warn
import json
import random
import string

from .base import ScenarioBase, ScenarioWithCharacters, ScenarioWithDialogue

from ..utils import toolbox

class Sentence():
	def __init__(self, text, info):
		self._text = text
		self._info = info
	@property
	def text(self):
		return self._text
	@text.setter
	def text(self, s):
		self._text = s
	@property
	def info(self):
		return self._info
	def update(self, text = None, info: Dict = None):
		if text is not None:
			self._text = text
		if info is not None:
			self._info.update(info)

class fixed_defaultdict(defaultdict):
	def __missing__(self, key):
		if self.default_factory is None:
			raise KeyError((key, ))
		value = self.default_factory()
		super().__setitem__(key, value)
		return value
	def __setitem__(self, key, value):
		raise TypeError("You cannot change the reference of the key.")
	def key_copy(self, n1, n2):
		super().__setitem__(n2, self.get(n1))

class DictSentenceInfo(MutableMapping):
	def __init__(self, sentence: Sentence):
		self._sentence = sentence
	def __getitem__(self, key):
		if key == 'text':
			return self._sentence.text
		return self._sentence.info[key]
	def __setitem__(self, key, i):
		if key == 'text':
			self._sentence.text = i
		else:
			self._sentence.info[key] = i
	def __delitem__(self, key):
		if key == 'text':
			raise KeyError("text cannot be deleted!")
		del self._sentence.info[key]
	def __iter__(self):
		yield 'text'
		yield from self._sentence.info
	def __len__(self):
		return 1 + len(self._sentence.info)
	def popitem(self):
		return self._sentence.info.popitem()
	def update(self, d = None, **kwargs):
		if d is not None:
			kwargs = d
		if 'text' in kwargs:
			self['text'] = kwargs.pop('text')
		self._sentence.info.update(kwargs)

class CharacterDict(Mapping):
	def __init__(self, d: defaultdict):
		self._d = d
	def __getitem__(self, key):
		if key not in self._d:
			raise KeyError(f'{key} is not a character name.')
		return self._d[key]
	def __iter__(self):
		return iter(self._d)
	def __len__(self):
		return len(self._d)

class DialogueDict(Mapping):
	def __init__(self, d: defaultdict):
		self._d = d
	def __getitem__(self, key):
		if key not in self._d:
			raise KeyError(f'{key} is not a handler.')
		return DictSentenceInfo(self._d[key])
	def __iter__(self):
		return iter(self._d)
	def __len__(self):
		return len(self._d)

class Scenario(ScenarioBase, ScenarioWithCharacters, ScenarioWithDialogue):
	_handler_generator = staticmethod(lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k = 16)))
	_base: str = 'gimi65536'
	_version: str = '0.0.2'
	_default_macrosignal = ':::'
	_default_macrosplit = '/'
	def __init__(self):
		self._macrosignal = self._default_macrosignal
		self._macrosplit = self._default_macrosplit
		self._title: str = ''
		self._other_info: dict = {}
		#self._character: Dict[str, dict] = fixed_defaultdict(dict)
		#self._dialogue: Dict[str, Sentence] = fixed_defaultdict(lambda: Sentence(text = "", info = {}))
		self._character: Dict[str, dict] = defaultdict(dict)
		self._dialogue: Dict[str, Sentence] = defaultdict(lambda: Sentence(text = "", info = {}))
		self._handler_list: list = []

		self._character_dict = CharacterDict(self._character)
		self._dialogue_dict = DialogueDict(self._dialogue)
	@property
	def base(self) -> str:
		return self._base
	@base.setter
	def base(self, i: str):
		raise AttributeError("""The property 'base' in gimi65536's Scenario format is read-only.""")
	@property
	def version(self) -> str:
		return self._version
	@version.setter
	def version(self, i: str):
		raise AttributeError("""The property 'version' in gimi65536's Scenario format is read-only.""")
	@property
	def macrosignal(self):
		return self._macrosignal
	@macrosignal.setter
	def macrosignal(self, i: str):
		self._macrosignal = i
	@property
	def macrosplit(self):
		return self._macrosplit
	@macrosplit.setter
	def macrosplit(self, i: str):
		self._macrosplit = i
	@property
	def title(self) -> str:
		return self._title
	@title.setter
	def title(self, i: str):
		self._title = i
	def encode(self, **kwargs):
		e = _encoder(**kwargs)
		d = {
			'Base': self.base,
			'Version': self.version,
			'MacroSignal': self._macrosignal,
			'MacroSplit': self._macrosplit,
			'Title': self.title,
			'ScenarioInfo': self.other_info,
			'Character': self._character,
			'Dialogue': [self._dialogue[h] for h in self._handler_list]}
		return e.encode(d)
	@classmethod
	def decode(cls, s, transformers: Dict[Tuple[str, str], Dict[Tuple[str, str], Callable]] = {}, **kwargs) -> Scenario:
		d = json.JSONDecoder(**kwargs)
		data = d.decode(s)
		sol = cls()
		if data['Base'] == 'gimi65536':
			#version update
			if data['Version'] == '0.0.1':
				data['MacroSignal'] = cls._default_macrosignal
				data['MacroSplit'] = cls._default_macrosplit
				data['Version'] = '0.0.2'

			#newest
			if data['Version'] != '0.0.2':
				#error
				pass
		else:
			f, t = (data['Base'], data['Version']), (cls._base, cls._version)
			data = transformers[f][t](data)
		sol.macrosignal = data['MacroSignal']
		sol.macrosplit = data["MacroSplit"]
		sol.title = data['Title']
		sol.other_info.update(data['ScenarioInfo'])
		sol._character.update(data['Character'])

		dialogue = data['Dialogue']
		n = len(dialogue)
		while len(sol._dialogue) < n:
			sol._dialogue[cls._handler_generator()]
		sol._handler_list = list(sol._dialogue.keys())
		for handler, dictdata in zip(sol._handler_list, dialogue):
			sol._dialogue[handler].update(text = dictdata['Text'], info = dictdata['Info'])

		return sol
	def save(self, file: IOBase, **kwargs):
		file.write(self.encode(**kwargs))
	@classmethod
	def load(cls, file: IOBase, transformers: Dict[Tuple[str, str], Dict[Tuple[str, str], Callable]] = {}, **kwargs) -> Scenario:
		s = file.read()
		return cls.decode(s, transformers, **kwargs)
	@property
	def other_info(self) -> dict:
		return self._other_info

	def create_character(self, name, **kwargs):
		if name not in self._character:
			self._character[name].update(**kwargs)
		else:
			warn(f"The character '{name}' cannot be overwritten!\nThe function did not modify anything.", UserWarning)
	def rename_character(self, n1, n2):
		if n2 in self._character:
			warn(f"The character '{n2}' cannot be overwritten by '{n1}'!\nThe function did not modify anything.", UserWarning)
			return
		#d = self._character.get(n1)
		#self._character[n2].update(d)
		#self._character.key_copy(n1, n2)
		self._character[n2] = self._character[n1]
		del self._character[n1]
	def modify_character(self, name, **kwargs):
		self._character.get(name).update(**kwargs)
	def character_info(self, name):
		return self._character.get(name)
	def delete_character(self, *names):
		for name in names:
			del self._character[name]
	@property
	def character(self) -> Mapping[str, MutableMapping]:
		return self._character_dict
	def character_names(self):
		return iter(self._character.keys())

	def insert_sentence(self, text, predefined_handler = None, **kwargs):
		if predefined_handler is None:
			handler = self._handler_generator()
		else:
			handler = predefined_handler
		while handler in self._dialogue:
			handler = self._handler_generator()
		self._dialogue[handler].update(text = text, info = kwargs)
		self._handler_list.append(handler)
		return handler
	def modify_sentence(self, handler, text = None, **kwargs):
		if isinstance(text, str):
			self._dialogue.get(handler).text = text
		self._dialogue.get(handler).info.update(**kwargs)
	def sentence_info(self, handler) -> DictSentenceInfo:
		return DictSentenceInfo(self._dialogue.get(handler))
	def delete_sentence(self, *handlers):
		d = {h: i for i, h in enumerate(self._handler_list)}
		handlers = sorted(handlers, key = lambda n: d[n])
		i, n = 0, len(handlers)
		l = []
		for handler in self._handler_list:
			if i < n and handler == handlers[i]:
				del self._dialogue[handler]
				i += 1
			else:
				l.append(handler)
		self._handler_list = l
	@property
	def dialogue(self) -> Mapping[str, MutableMapping]:
		return self._dialogue_dict
	def get_sentence_order(self, handler):
		return self._handler_list.index(handler)
	def set_sentence_order(self, handler, neworder):
		self._handler_list.remove(handler)
		self._handler_list.insert(neworder, handler)
	def batch_get_sentence_order(self, handlers):
		'''
		Maybe O(|_handler_list|) amortized, better than loop calling get
		'''
		reverse_index = {handlers: i for i, handlers in enumerate(self._handler_list)}
		return [reverse_index[h] for h in handlers]
	def batch_set_sentence_order(self, handlers, neworders):
		'''
		Let N be |_handler_list| and h be |handlers|
		neworders: list of integers between 0 and N - 1
		'''
		N = len(self._handler_list)
		d = {}
		#build valid table, O(h) amortized
		for h, o in zip(handlers, neworders):
			if o >= 0 and o < N and o not in d:
				d[o] = h
		valid_h = set(d.values()) #O(h) amortized
		#split
		stay, move = [], [d[i] for i in sorted(d.keys())] #O(hlogh)
		#O(N) amortized
		for h in _handler_list:
			if h not in valid_h: #valid_h is hash set
				stay.append(h)
		moved_handlers = move.copy()

		#intersect
		result = []
		#O(N) amortized
		for i in range(N):
			if i not in d:
				result.append(stay.pop())
			else:
				result.append(move.pop())

		self._handler_list = result
		return moved_handlers
	def swap_sentence_order(self, h1, h2):
		i, j = self._handler_list.index(h1), self._handler_list.index(h2)
		self._handler_list[i], self._handler_list[j] = self._handler_list[j], self._handler_list[i]
	def increment_sentence_order(self, handler):
		#i = self.get_sentence_order(handler)
		#if i == 0:
		#	return
		#self._handler_list[i], self._handler_list[i - 1] = self._handler_list[i - 1], self._handler_list[i]
		self.batch_increment_sentence_order([handler])
	def decrement_sentence_order(self, handler):
		#i = self.get_sentence_order(handler)
		#if i == len(self._handler_list) - 1:
		#	return
		#self._handler_list[i], self._handler_list[i + 1] = self._handler_list[i + 1], self._handler_list[i]
		self.batch_decrement_sentence_order([handler])
	def batch_increment_sentence_order(self, handlers):
		return self._batch_reorder_sentence_order(handlers, up = True)
	def batch_decrement_sentence_order(self, handlers):
		return self._batch_reorder_sentence_order(handlers, up = False)
	def _batch_reorder_sentence_order(self, handlers, up):
		index = self.batch_get_sentence_order(handlers)
		moved_index = [i + (-1 if up else 1) for i in index]
		return self.batch_set_sentence_order(handlers, moved_index)
	def __deprecated_batch_reorder_sentence_order(self, handlers, up):
		handlers = list(set(handlers))
		d = {h: i for i, h in enumerate(self._handler_list)}
		sorted_h_o_index_list = [(h, d[h], i) for i, h in enumerate(sorted(handlers, key = lambda n: d[n]))] #h o i
		#(handler name, the handler is in o'th place among total sentences, in i'th place of the 'handlers' param)
		#if up, o == i should be dropped
		#if down, o - i == len(self._handler_list) - len(handlers) should be dropped
		#erase the top/bottom element, they don't need to be in/decremented
		l = [i[1] for i in sorted_h_o_index_list]
		mapped = toolbox.shift(l, len(self._handler_list), up)
		'''
		if up:
			ite = dropwhile((lambda t: t[1] == t[2]), sorted_h_o_index_list)
		else:
			ite = takewhile((lambda t: t[1] - t[2] != len(self._handler_list) - len(handlers)), sorted_h_o_index_list)
			ite = reversed(list(ite))
		'''
		ite = iter(sorted_h_o_index_list) if up else reversed(sorted_h_o_index_list)
		sol = []
		for h, o, _ in ite:
			#target = (o - 1 if up else o + 1)
			target = mapped[o]
			if o == target:
				continue
			sol.append(h)
			self._handler_list[o], self._handler_list[target] = self._handler_list[target], self._handler_list[o]
		return sol #the handlers really re-ordered stored in the processing order
	def handlers(self):
		return iter(self._handler_list)

class _encoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Sentence):
			return {'Text': obj.text, 'Info': obj.info}
		return json.JSONEncoder.default(self, obj)

if __name__ == '__main__':
	s = Scenario()
	s.create_character("wayne")
	s.create_character("zeng")
	s.insert_sentence("fuck you!")
	h = s.insert_sentence("shit!")
	s.increment_sentence_order(h)
	s.increment_sentence_order(h)
	text = s.encode(indent = '\t')
	t = Scenario.decode(text)
	s.decrement_sentence_order(h)
	s.decrement_sentence_order(h)
	print(s.encode(indent = '\t'))
	print(t.encode(indent = '\t'))
	print(*s.character_names())
	with open('test.json', 'w', encoding = 'utf-8') as file:
		s.save(file, indent = '\t')