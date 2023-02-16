from collections import namedtuple
from copy import copy
import tkinter as tk

from .memento import Originator, Memento, NotRestorableError

from ..scenario.base import ScenarioBase

EditorEvent = namedtuple('EditorEvent', ('description', 'action', 'key', 'before', 'after'))

class BaseEditorView(tk.Frame):
	def __init__(self, master, *args, **kwargs):
		tk.Frame.__init__(self, master, *args, **kwargs)

class BaseEditor(Originator):
	defaultinfo = {}
	def __init__(self, master, *args, viewClass = BaseEditorView, **kwargs):
		view = viewClass(master, *args, **kwargs)

		self.view = view
		self._scenario = None
		self._callback = lambda e: None
	def load_scenario(self, scenario: ScenarioBase):
		'''
		load the scenario and build the editor UI
		'''
		pass
	def upload_to_scenario(self):
		'''
		used to update some lazy changes
		'''
		pass
	@classmethod
	def expand_info(cls, info):
		changed = False
		for key in cls.defaultinfo.keys():
			if key not in info:
				changed = True
				info[key] = copy(cls.defaultinfo[key])
		return changed
	@property
	def callback(self):
		return self._callback
	@callback.setter
	def callback(self, f):
		self._callback = f

class BaseLoadAdaptMemento(Memento):
	def __init__(self):
		self.changed = True
	def rollback(self):
		if self.changed:
			raise NotRestorableError