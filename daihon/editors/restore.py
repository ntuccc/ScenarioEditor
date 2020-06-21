from .memento import *
from typing import List

class RestoreManager(Caretaker):
	_l: List[Memento]
	_MAXIMUM = 50
	def __init__(self):
		self._l = []
	def push(self, m):
		if len(self._l) >= self._MAXIMUM:
			self._l.pop()
		self._l.append(m)
		self._push_callback(m)
	def set_push_callback(self, f):
		self._push_callback = f
	def restore_pop(self):
		m = self._l.pop()
		try:
			m.executor.restore_from_memento(m)
		except NotRestorableError:
			self._l.append(m)
			return False
		self._restore_callback(m)
		return True
	def set_restore_callback(self, f):
		self._restore_callback = f
	def reset(self):
		self._l.clear()