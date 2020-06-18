import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext

from .base_editor import BaseEditor, EditorEvent

from ..scenario.base import ScenarioWithCharacters, ScenarioWithDialogue

class InfoEditor(BaseEditor):
	defaultinfo = {'index': '', 'date': '', 'image': '', 'imagelist': ''}
	def __init__(self, master, *args, **kwargs):
		super().__init__(master, *args, **kwargs, class_ = 'InfoEditor')
		
		main_frame = tk.Frame(self)

		self._title_var = tk.StringVar(main_frame)
		self._index_var = tk.StringVar(main_frame)
		self._date_var = tk.StringVar(main_frame)
		self._image_var = tk.StringVar(main_frame)
		self._imagelist_var = tk.StringVar(main_frame)
		...

		title_label = tk.Label(main_frame, text = '標題')
		title_entry = tk.Entry(main_frame, textvariable = self._title_var)
		index_label = tk.Label(main_frame, text = '編號')
		index_entry = tk.Entry(main_frame, textvariable = self._index_var)
		date_label = tk.Label(main_frame, text = '日期')
		date_entry = tk.Entry(main_frame, textvariable = self._date_var)
		image_label = tk.Label(main_frame, text = '圖檔')
		image_entry = tk.Entry(main_frame, textvariable = self._image_var)
		imagelist_label = tk.Label(main_frame, text = '填充圖檔')
		imagelist_entry = tk.Entry(main_frame, textvariable = self._imagelist_var)
		...
		...

		title_label.grid(row = 0, column = 0, padx = 20)
		title_entry.grid(row = 0, column = 1)
		index_label.grid(row = 1, column = 0, padx = 20)
		index_entry.grid(row = 1, column = 1)
		date_label.grid(row = 2, column = 0, padx = 20)
		date_entry.grid(row = 2, column = 1)
		image_label.grid(row = 3, column = 0, padx = 20)
		image_entry.grid(row = 3, column = 1)
		imagelist_label.grid(row = 4, column = 0, padx = 20)
		imagelist_entry.grid(row = 4, column = 1)
		...
		...

		main_frame.pack(expand = True, fill = tk.BOTH)

		button_frame = tk.Frame(self)

		upload = tk.Button(button_frame, text = '套用變更', command = self._apply)
		cancel = tk.Button(button_frame, text = '還原變更', command = self.fetch_info)

		upload.grid(row = 0, column = 0)
		cancel.grid(row = 0, column = 1)

		button_frame.pack(expand = True, fill = tk.X)
	def load_scenario(self, scenario):
		'''
		load the scenario and build the editor UI
		'''
		self._scenario = scenario
		self._adapt_info()
		self.fetch_info()
	def _apply(self):
		info = self._scenario.other_info
		ori = (
			self._scenario.title,
			info['index'],
			info['date'],
			info['image'],
			info['imagelist']
			#...
		)
		now = (
			self._title_var.get(),
			self._index_var.get(),
			self._date_var.get(),
			self._image_var.get(),
			self._imagelist_var.get()
			#...
		)
		if ori == now:
			return

		self._scenario.title = self._title_var.get()
		info['index'] = self._index_var.get()
		info['date'] = self._date_var.get()
		info['image'] = self._image_var.get()
		info['imagelist'] = self._imagelist_var.get()
		...

		self.callback(EditorEvent(description = 'InfoEditor', action = 'UpdateInfo', key = None, before = ori, after = now))
	def fetch_info(self):
		info = self._scenario.other_info

		self._title_var.set(self._scenario.title)
		self._index_var.set(info['index'])
		self._date_var.set(info['date'])
		self._image_var.set(info['image'])
		self._imagelist_var.set(info['imagelist'])
		...
	def _adapt_info(self):
		"""
		only called when loading
		"""
		changed = False
		info = self._scenario.other_info
		if self.expand_info(info) is True:
			changed = True
		if changed:
			self.callback(EditorEvent(description = 'InfoEditor', action = 'LoadAdapt', key = None, before = None, after = None))