from abstract_classes import ScenarioBase
from collections import namedtuple
from copy import copy
import tkinter as tk

EditorEvent = namedtuple('EditorEvent', ('description', 'action', 'key', 'before', 'after'))

class BaseEditor(tk.Frame):
	defaultinfo = {}
	def __init__(self, master, *args, **kwargs):
		super().__init__(master, *args, **kwargs)
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