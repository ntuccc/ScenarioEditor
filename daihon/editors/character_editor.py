import tkinter as tk
import warnings
from itertools import count
from tkinter import colorchooser, ttk
from typing import Optional
from warnings import warn

from .base import BaseEditor, BaseEditorView, EditorEvent

from ..scenario.base import ScenarioWithCharacters

defaultcolor = '#ff0000'

additional_info = {
	'abbreviated': {'name': '簡稱', 'width': 5, 'default': ''},
	'gender': {'name': '性別', 'width': 5, 'default': '♀'},
	'cast': {'name': '聲優', 'width': 12, 'default': ''},
}

class CharacterEditorView(BaseEditorView):
	def __init__(self, master, *args, **kwargs):
		super().__init__(master, *args, **kwargs, class_ = 'CharacterEditor')

		self._list_frame = tk.Frame(self)
		self._modify_frame = tk.Frame(self)

		self._list_frame.pack(side = tk.LEFT, fill = tk.Y)
		self._modify_frame.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)

		self._build_list()
	def _build_list(self):
		scrollbar = tk.Scrollbar(self._list_frame, orient=tk.VERTICAL)
		self._listbox = tk.Listbox(self._list_frame, selectmode = tk.BROWSE, yscrollcommand=scrollbar.set)
		scrollbar.config(command=self._listbox.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		self._listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
	def build_modification(self):
		NotImplemented

class CharacterEditor(BaseEditor):
	defaultinfo = {n: d.get('default', '') for n, d in additional_info.items()}
	def __init__(self, master, *args, **kwargs):
		super().__init__(master, *args, viewClass = CharacterEditorView, **kwargs)

		self.view.build_modification()
	def load_scenario(self, scenario: ScenarioWithCharacters):
		self._scenario = scenario
		#ori_frames_number = len(self._charaframes)
		self._adapt_info()

		characters = scenario.character
		no_order_chara = []
		chara_order = {}
		for name in characters:
			info = scenario.character_info(name)
			if 'order' not in info:
				no_order_chara.append(name)
			else:
				chara_order[name] = info['order']
		order = sorted(chara_order.keys(), key = lambda n: chara_order[n])
		order.extend(no_order_chara)

	def upload_to_scenario(self):
		"""
		The only place where order updates
		"""
		for i, node in enumerate(self._charaframes_list):
			self._scenario.character_info(node.value.name)['order'] = i

		for chara_frame in self._listframe.winfo_children():
			if chara_frame.winfo_class() == 'CharacterFrame':
				chara_frame.namefocusin_check()
	def _adapt_info(self):
		"""
		only called when loading
		"""
		changed = False
		for name in self._scenario.character.keys():
			info = self._scenario.character_info(name)
			if self.expand_info(info) is True:
				changed = True
		if changed:
			self.save_memento(action = 'LoadAdapt',  detail ={})
	@staticmethod
	def destroy_node(l, node):
		print(455)
		node.value.pack_forget()
		node.value.destroy()
		l.remove(node)
	@classmethod
	def expand_info(cls, character_info):
		changed = False
		if 'color' not in character_info:
			character_info['color'] = defaultcolor
			changed = True
		changed = super().expand_info(character_info) or changed
		return changed
	def add_character(self):
		if self._scenario is None:
			warn("add_character() fails: no scenario loaded.", UserWarning)
			return
		name = self._newcharaframe.name
		if len(name) == 0:
			return
		elif name in self._scenario.character:
			return
		newinfo = {'color': self._newcharaframe.color}
		self.expand_info(newinfo)

		self._scenario.create_character(name, **newinfo)

		self._add_chara_tail(name, self._scenario.character_info(name))
		self._newcharaframe.name = ''

		self.save_memento(action = 'NewChara', detail = {'key': name, 'before': name, 'after': name})
	def del_character(self, node):
		name = node.value.name
		self.destroy_node(self._charaframes_list, node)
		self._scenario.delete_character(name)
		self.save_memento(action = 'DeleteChara', detail = {'key': name, 'before': name, 'after': None})
	def move_order(self, node, mode):
		if mode not in ('up', 'down'):
			return
		if mode == 'up':
			if node.prev is None:
				return
			another = node.prev
		else:
			if node.next is None:
				return
			another = node.next
		self.save_memento(action = 'MoveChara', detail = {'key': node.value.name, 'before': None, 'after': mode})
		node.value.name, another.value.name = another.value.name, node.value.name
		node.value.character_info_modify(self._scenario.character_info(node.value.name))
		another.value.character_info_modify(self._scenario.character_info(another.value.name))
	def rename_character(self, n1, n2):
		success = True
		with warnings.catch_warnings():
			warnings.filterwarnings('error')
			try:
				self._scenario.rename_character(n1, n2)
			except UserWarning:
				success = False
		if success:
			self.save_memento(action = 'RenameChara', detail = {'key': (n1, n2), 'before': n1, 'after': n2})
		return success

if __name__ == '__main__':
	from scenario import Scenario
	from tkinter import font
	import gc
	gc.set_debug(gc.DEBUG_UNCOLLECTABLE)
	t = tk.Tk()
	f = font.nametofont("TkDefaultFont")
	#f = font.Font(t, family = "微軟正黑體", size = 9)
	t.option_add("*font", f)
	c = CharacterEditor(t)
	c.pack()
	with open('test.json', encoding = 'utf-8') as file:
		s = Scenario.load(file)
	with open('basetest.json', encoding = 'utf-8') as file:
		s0 = Scenario.load(file)
	c.callback = lambda e: print(e)
	c.load_scenario(s)
	#c.load_scenario(s0)
	c.upload_to_scenario()
	c.mainloop()
	#pass
	print(gc.collect())
	print(gc.garbage)