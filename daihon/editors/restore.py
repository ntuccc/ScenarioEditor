from .memento import *

class RestoreManager(Caretaker):
	_l: List[Memento]
	_MAXIMUM = 50
	def __init__(self):
		self._l = []
	def push(self, m):
		if len(self._l) >= _MAXIMUM:
			self._l.pop()
		self._l.append(m)
	def restore_pop(self):
		m = self._l.pop()
		try:
			m.executor.restore_from_memento(m)
		except NotRestorableError:
			self._l.append(m)
			return False
		return True
	def reset(self):
		self._l.clear()