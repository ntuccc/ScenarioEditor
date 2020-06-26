import tkinter as tk
from functools import partial
from itertools import count
from tkinter import ttk, messagebox, simpledialog, scrolledtext

from .base import BaseEditor, BaseEditorView, BaseLoadAdaptMemento
from .memento import Memento

from ..scenario.base import ScenarioWithCharacters, ScenarioWithDialogue

class InfoEditorView(BaseEditorView):
	def __init__(self, master, *args, **kwargs):
		super().__init__(master, *args, **kwargs, class_ = 'InfoEditor')

		self._main_frame = tk.Frame(self)
		self._button_frame = tk.Frame(self)

		self._main_frame.pack(expand = True, fill = tk.BOTH)
		self._button_frame.pack(expand = True, fill = tk.X)

		self._entry_counter = count()
		self._button_counter = count()
	def add_entry(self, text):
		i = next(self._entry_counter)

		var = tk.StringVar(self._main_frame)
		label = tk.Label(self._main_frame, text = text)
		entry = tk.Entry(self._main_frame, textvariable = var)

		label.grid(row = i, column = 0, padx = 20)
		entry.grid(row = i, column = 1)

		return var
	def add_button(self, text, command):
		i = next(self._button_counter)

		b = tk.Button(self._button_frame, text = text, command = command)
		b.grid(row = 0, column = i)

class InfoEditor(BaseEditor):
	defaultinfo = {'index': '', 'date': '', 'image': '', 'imagelist': ''}
	def __init__(self, master, *args, **kwargs):
		super().__init__(master, *args, viewClass = InfoEditorView, **kwargs)

		self.entries = [
			{
				'name': '標題',
				'getter': self._get_title,
				'setter': self._set_title,
			},
			{
				'name': '編號',
				'getter': partial(self._get_info, 'index'),
				'setter': partial(self._set_title, 'index'),
			},
			{
				'name': '日期',
				'getter': partial(self._get_info, 'date'),
				'setter': partial(self._set_title, 'date'),
			},
			{
				'name': '圖檔',
				'getter': partial(self._get_info, 'image'),
				'setter': partial(self._set_title, 'image'),
			},
			{
				'name': '填充圖檔',
				'getter': partial(self._get_info, 'imagelist'),
				'setter': partial(self._set_title, 'imagelist'),
			},
			#...
		]

		self._add_entries()
		self._add_buttons()
	def load_scenario(self, scenario):
		'''
		load the scenario and build the editor UI
		'''
		self._scenario = scenario
		self._adapt_info()
		self.fetch_info()
	def _add_entries(self):
		entries = self.entries

		for d in entries:
			var = self.view.add_entry(d['name'])
			d['var'] = var
	def _add_buttons(self):
		#simple
		self.view.add_button(text = '套用變更', command = self._apply)
		self.view.add_button(text = '還原變更', command = self.fetch_info)
	def _get_title(self):
		return self._scenario.title
	def _get_info(self, info):
		reutrn self._scenario.other_info[info]
	def _set_title(self, title):
		self._scenario.title = title
	def _set_info(self, info, value):
		self._scenario.other_info[info] = value
	def _apply(self):
		try:
			memento = UpdateInfoMemento(self.entries)
		except NoNeedApplyError:
			return

		self.save_memento(m)
	def apply_info(self):
		for d in self.entries:
			d['setter'](d['var'].get())
	def fetch_info(self):
		for d in self.entries:
			d['var'].set(d['getter']())
	def _adapt_info(self):
		"""
		only called when loading
		"""
		self.save_memento(LoadAdaptInfoMemento(self._scenario))

class NoNeedApplyError(ValueError):
	pass

class UpdateInfoMemento(Memento):
	def __init__(self, entries):
		super().__init__()

		self.entries = entries

		ori = tuple(d['getter']() for d in self.entries)
		now = tuple(d['var'].get() for d in self.entries)

		if ori == now:
			raise NoNeedApplyError
		self.ori, self.now = ori, now
	def execute(self):
		for d, v in zip(self.entries, self.now):
			d['setter'](v)
	def rollback(self):
		for d, v in zip(self.entries, self.ori):
			d['setter'](ori)

class LoadAdaptInfoMemento(BaseLoadAdaptMemento):
	def __init__(self, scenario):
		self.scenario = scenario
	def execute(self):
		self.changed = False
		info = self._scenario.other_info
		if self.expand_info(info) is True:
			self.changed = True