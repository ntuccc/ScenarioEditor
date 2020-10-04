from __future__ import annotations
from abc import ABCMeta, abstractmethod
from collections.abc import Mapping, MutableMapping, Iterator, Collection
from io import IOBase
from typing import Dict, Callable

class ScenarioBase(metaclass = ABCMeta):
	# (base, version) denotes the json format instead of Scenario class
	@property
	@abstractmethod
	def base(self) -> str:
		raise NotImplementedError
	@base.setter
	@abstractmethod
	def base(self, i: str):
		raise NotImplementedError
	@property
	@abstractmethod
	def version(self):
		raise NotImplementedError
	@version.setter
	@abstractmethod
	def version(self, i):
		raise NotImplementedError
	@property
	@abstractmethod
	def title(self) -> str:
		raise NotImplementedError
	@title.setter
	@abstractmethod
	def title(self, i: str):
		raise NotImplementedError
	#@property
	#@abstractmethod
	#def date(self):
	#	raise NotImplementedError
	#@date.setter
	#@abstractmethod
	#def date(self, i):
	#	raise NotImplementedError
	#@abstractmethod
	#def load(self, file, **kwargs):
	#	raise NotImplementedError
	@abstractmethod
	def encode(self, **kwargs):
		raise NotImplementedError
	@classmethod
	@abstractmethod
	def decode(cls, s, transformers: Dict[tuple, Dict[tuple, Callable]] = None, **kwargs) -> ScenarioBase:
		'''
		transformer:
			dict, key: (base, version) indicating the origin format
				  value: dict, key: (base, version) indicating the targetted format
				  			   value: a function
		'''
		raise NotImplementedError
	@abstractmethod
	def save(self, file: IOBase, **kwargs):
		raise NotImplementedError
	@classmethod
	@abstractmethod
	def load(cls, file: IOBase, transformers: Dict[tuple, Dict[tuple, Callable]] = None, **kwargs) -> ScenarioBase:
		raise NotImplementedError
	@property
	@abstractmethod
	def other_info(self) -> MutableMapping:
		raise NotImplementedError

class ScenarioWithCharacters(metaclass = ABCMeta):
	@abstractmethod
	def create_character(self, name, **kwargs):
		raise NotImplementedError
	@abstractmethod
	def rename_character(self, n1, n2):
		raise NotImplementedError
	@abstractmethod
	def modify_character(self, name, **kwargs):
		raise NotImplementedError
	@abstractmethod
	def character_info(self, name) -> MutableMapping:
		"""
		You can access and modify the info by the returned object
		"""
		raise NotImplementedError
	@abstractmethod
	def delete_character(self, *names):
		raise NotImplementedError
	@property
	@abstractmethod
	def character(self) -> Mapping:
		"""
		You can access the info by __getitem__(name) or [name] of the returned object
		equivalent to character_info(name)
		"""
		raise NotImplementedError
	@abstractmethod
	def character_names(self) -> Iterator:
		raise NotImplementedError

#use character info or additional array variable to deal with order
class ScenarioWithCharactersOrdered(ScenarioWithCharacters):
	@abstractmethod
	def get_character_order(self, name):
		raise NotImplementedError
	@abstractmethod
	def set_character_order(self, name, neworder):
		raise NotImplementedError
	@abstractmethod
	def swap_character_order(self, n1, n2):
		raise NotImplementedError
	@abstractmethod
	def increment_character_order(self, name):
		raise NotImplementedError
	@abstractmethod
	def decrement_character_order(self, name):
		raise NotImplementedError
	@abstractmethod
	def batch_increment_character_order(self, names: Collection) -> list:
		raise NotImplementedError
	@abstractmethod
	def batch_decrement_character_order(self, names: Collection) -> list:
		raise NotImplementedError

class ScenarioWithDialogue(metaclass = ABCMeta):
	@abstractmethod
	def insert_sentence(self, text, predefined_handler = None, **kwargs):
		# return a handler
		raise NotImplementedError
	@abstractmethod
	def modify_sentence(self, handler, text, **kwargs):
		raise NotImplementedError
	@abstractmethod
	def sentence_info(self, handler) -> MutableMapping:
		"""
		You can access and modify the info by the returned object
		"""
		raise NotImplementedError
	@abstractmethod
	def delete_sentence(self, *handlers):
		raise NotImplementedError
	@property
	@abstractmethod
	def dialogue(self) -> Mapping:
		"""
		You can access the info by __getitem__(handler) or [handler] of the returned object
		equivalent to sentence_info(handler)
		"""
		raise NotImplementedError
	@abstractmethod
	def get_sentence_order(self, handler):
		raise NotImplementedError
	@abstractmethod
	def set_sentence_order(self, handler, neworder):
		raise NotImplementedError
	@abstractmethod
	def batch_get_sentence_order(self, handlers):
		raise NotImplementedError
	@abstractmethod
	def batch_set_sentence_order(self, handlers, neworders):
		raise NotImplementedError
	@abstractmethod
	def swap_sentence_order(self, h1, h2):
		raise NotImplementedError
	@abstractmethod
	def increment_sentence_order(self, handler):
		raise NotImplementedError
	@abstractmethod
	def decrement_sentence_order(self, handler):
		raise NotImplementedError
	@abstractmethod
	def batch_increment_sentence_order(self, handlers: Collection) -> list:
		raise NotImplementedError
	@abstractmethod
	def batch_decrement_sentence_order(self, handlers: Collection) -> list:
		raise NotImplementedError
	@abstractmethod
	def handlers(self) -> Iterator:
		raise NotImplementedError