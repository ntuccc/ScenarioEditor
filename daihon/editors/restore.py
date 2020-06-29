from .memento import *
from ..utils.decorators import callbackmethod
from typing import List

class RestoreManager(Caretaker):
	_l: List[Memento]
	_MAXIMUM = 50
	def __init__(self):
		self._l = []
	@callbackmethod
	def push(self, m):
		m.execute()
		if len(self._l) >= self._MAXIMUM:
			self._l.pop()
		self._l.append(m)
		return m
	@callbackmethod
	def restore_pop(self):
		try:
			m = self._l.pop()
		except IndexError:
			#nothing to pop
			raise NotRestorableError
		try:
			m.rollback()
		except NotRestorableError as e:
			self._l.append(m)
			raise e
		return m
	def reset(self):
		self._l.clear()