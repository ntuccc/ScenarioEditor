from __future__ import annotations
from dataclasses import dataclass

class Originator:
	_caretaker: Caretaker
	def set_caretaker(self, c):
		self._caretaker = c
	def save_memento(self, action: str, detail: dict):
		memento = Memento(self, action, detail)
		if hasattr(self, '_caretaker') and self._caretaker is not None:
			self._caretaker.push(memento)
		return memento
	def restore_from_memento(self, m: Memento):
		raise NotImplementedError

@dataclass
class Memento:
	executor: Originator
	action: str
	detail: dict

class Caretaker:
	def push(self, m: Memento):
		raise NotImplementedError
	def restore_pop(self):
		raise NotImplementedError
	def reset(self):
		raise NotImplementedError

class NotRestorableError(ValueError):
	'''
	An originator raises this error
	when a memento points to a non-restorable action
	and trace back to the state before restoration.
	'''
	pass