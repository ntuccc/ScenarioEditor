from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

T = TypeVar('T')

@dataclass
class listnode(Generic[T]):
	value: T
	prev: Optional[listnode] = None
	next: Optional[listnode] = None
	def remove(self):
		if self.prev is not None:
			self.prev.next = self.next
		if self.next is not None:
			self.next.prev = self.prev
		self.prev = self.next = None
	def __repr__(self):
		return f"listnode({repr(self.value)})"

class linkedlist(Generic[T]):
	"""
	This class is to maintain head and tail
	"""
	def __init__(self):
		self._head: Optional[listnode[T]] = None
		self._tail: Optional[listnode[T]] = None
	def __iter__(self):
		node = self._head
		while node is not None:
			yield node
			node = node.next
	def append_head(self, node: listnode[T]):
		if self._head is None:
			self._head = self._tail = node
		else:
			self._head.prev = node
			node.next = self._head
			self._head = node
	def append_tail(self, node: listnode[T]):
		if self._tail is None:
			self._head = self._tail = node
		else:
			self._tail.next = node
			node.prev = self._tail
			self._tail = node
	def remove(self, node: listnode[T]):
		if node is self._head:
			self._head = node.next
		if node is self._tail:
			self._tail = node.prev
		node.remove()
	@property
	def head(self):
		return self._head
	@property
	def tail(self):
		return self._tail
	def __repr__(self):
		l, node = [], self._head
		while node is not None:
			l.append(node)
			node = node.next
		return repr(l)

if __name__ == '__main__':
	l = linkedlist()
	print(linkedlist[int])