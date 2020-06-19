from __future__ import annotations
from dataclasses import dataclass
from typing import Any

class Originator:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	_caretaker: Caretaker
	def set_caretaker(self, c):
		self._caretaker = c
	def save_memento(self, action: str, d: dict):
		memento = Memento(self, action, d)
		if hasattr(self, '_caretaker') or self._caretaker is not None:
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