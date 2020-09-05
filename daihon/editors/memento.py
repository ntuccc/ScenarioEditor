from __future__ import annotations

#object for memento and two commands
class Memento:
	def __init__(self, detail = None, *, execute = None, rollback = None):
		if detail is None:
			detail = {}
		self.detail = detail
		if execute is not None:
			self.execute = execute
		if rollback is not None:
			self.rollback = rollback
	def execute(self):
		raise NotImplementedError
	def rollback(self):
		raise NotRestorableError

class Originator:
	_caretaker: Caretaker
	def set_caretaker(self, c):
		self._caretaker = c
	def save_memento(self, m: Memento):
		if hasattr(self, '_caretaker') and self._caretaker is not None:
			self._caretaker.push(m)
		return m
	'''
	def save_memento(self, action: str, detail: dict):
		memento = Memento(self, action, detail)
		if hasattr(self, '_caretaker') and self._caretaker is not None:
			self._caretaker.push(memento)
		return memento
	def restore_from_memento(self, m: Memento):
		raise NotImplementedError
	'''

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