import tkinter as tk
import warnings
from functools import partial
from itertools import count
from tkinter import colorchooser, ttk
from typing import Optional
from warnings import warn

from .base import BaseEditor, BaseEditorView, BaseLoadAdaptMemento
from .memento import Memento

from ..scenario.base import ScenarioWithCharacters

defaultcolor = '#ff0000'

additional_info = {
	'abbreviated': {'name': '簡稱', 'width': 5, 'default': ''},
	'gender': {'name': '性別', 'width': 5, 'default': '♀'},
	'cast': {'name': '聲優', 'width': 12, 'default': ''},
}

class _Var:
	def __init__(self, obj: tk.StringVar):
		self.obj = obj
	def get(self):
		return self.obj.get()
	def set(self, s):
		self.obj.set(s)
	def clear(self):
		self.set('')

class _Color_Var(_Var):
	def __init__(self, obj: tk.Label, init):
		self.obj = obj
		self.color = init
	def get(self):
		return self.color
	def set(self, s):
		self.color = s
		self.obj['bg'] = s
	def clear(self):
		self.set('#ffffff')

class CharacterEditorView(BaseEditorView):
	def __init__(self, master, *args, **kwargs):
		super().__init__(master, *args, **kwargs, class_ = 'CharacterEditor')

		self._list_frame = tk.Frame(self)
		self._modify_frame = tk.Frame(self)

		self._list_frame.pack(side = tk.LEFT, fill = tk.Y)
		self._modify_frame.pack(side = tk.RIGHT, expand = True, anchor = 'nw')

		self.labelvars = {}
		self.editvars = {}

		self._enable = []
	def build_list(self, add_command, del_command, up_command, down_command):
		box_frame = tk.Frame(self._list_frame)
		scrollbar = tk.Scrollbar(box_frame, orient=tk.VERTICAL)
		self.listbox = tk.Listbox(box_frame, selectmode = tk.BROWSE, yscrollcommand=scrollbar.set, activestyle = tk.NONE)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		self.listbox.pack(side=tk.LEFT, fill=tk.Y, expand=True)
		box_frame.pack(side = tk.TOP, fill = tk.Y, expand = True)

		button_frame = tk.Frame(self._list_frame)
		add_button = tk.Button(button_frame, text = '新增', command = add_command)
		del_button = tk.Button(button_frame, text = '刪除', command = del_command)
		add_button.grid(row = 0, column = 0)
		del_button.grid(row = 0, column = 1, padx = 10)
		button_frame.pack()

		self._enable.append(del_button)
	def build_modification(self, info, command):
		assert 'name' in info

		for i in info:
			d = info[i]
			assert 'name' in d

			frame = tk.Frame(self._modify_frame)
			label = tk.Label(frame, text = d['name'])
			label.grid(row = 0, column = 0, sticky = 'w')
			modify_label = tk.Label(frame, text = f'編輯{d["name"]}')
			modify_label.grid(row = 1, column = 0, pady = 2, sticky = 'w')

			typeof = d.get('type', 'text')
			if typeof == 'text':
				labelvar = tk.StringVar(frame)
				editvar = tk.StringVar(frame)

				labeltext = tk.Label(frame, textvariable = labelvar)
				entry = tk.Entry(frame, textvariable = editvar)

				self._enable.append(entry)

				labeltext.grid(row = 0, column = 1, sticky = 'w')
				entry.grid(row = 1, column = 1, sticky = 'w')

				self.labelvars[i] = _Var(labelvar)
				self.editvars[i] = _Var(editvar)
			elif typeof == 'color':
				labeltext = tk.Label(frame, text = '　', bg = '#ffffff')
				entry = tk.Label(frame, text = '　', bg = '#ffffff')

				labelvar = _Color_Var(labeltext, '#ffffff')
				editvar = _Color_Var(entry, '#ffffff')

				labeltext.grid(row = 0, column = 1)
				entry.grid(row = 1, column = 1)

				button = tk.Button(frame, text = '挑選顏色', command = partial(self.colorchoose, editvar))
				button.grid(row = 1, column = 2)
				self._enable.append(button)

				self.labelvars[i] = labelvar
				self.editvars[i] = editvar
			else:
				NotImplemented
			frame.pack(anchor = 'nw')
		button = tk.Button(self._modify_frame, text = '更改', command = command)
		self._enable.append(button)
		button.pack(anchor = 'se')
	def enable(self):
		for i in self._enable:
			i['state'] = tk.NORMAL
	def disable(self):
		for i in self._enable:
			i['state'] = tk.DISABLED
	def clear(self):
		for var in self.labelvars.values():
			var.clear()
		for var in self.editvars.values():
			var.clear()
	@staticmethod
	def colorchoose(color_var):
		_, hx = colorchooser.askcolor()
		if hx is not None:
			color_var.set(hx)


info = {
	'name': {'name': '名稱', 'type': 'text', 'default': None},
	'color': {'name': '顏色', 'type': 'color', 'default': '#ff0000'},
	'gender': {'name': '簡稱', 'type': 'text', 'default': ''},
	'abbreviated': {'name': '性別', 'type': 'text', 'default': ''},
	'cast': {'name': '聲優', 'type': 'text', 'default': ''}
}

class CharacterEditor(BaseEditor):
	defaultinfo = {n: d.get('default', '') for n, d in info.items() if n != 'name'}
	def __init__(self, master, *args, **kwargs):
		super().__init__(master, *args, viewClass = CharacterEditorView, **kwargs)
		self.info = info

		self._selection = None

		self.view.build_list(self.add_character, self.del_character, (lambda: NotImplemented), (lambda: NotImplemented))
		self.view.build_modification(info, (lambda: NotImplemented))
		self.view.disable()

		self.listbox = self.view.listbox

		self.listbox.bind('<<ListboxSelect>>', self._onselect)
	def load_scenario(self, scenario: ScenarioWithCharacters):
		self._scenario = scenario
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

		self.view.listbox.insert('end', *order)
	def upload_to_scenario(self):
		"""
		The only place where order updates
		"""
		for i, name in enumerate(self.view.listbox.get(0, 'end')):
			self._scenario.character_info(name)['order'] = i
	def _onselect(self, *args):
		if not self._scenario:
			return
		view = self.view
		self._selection = None #do not trigger the trace of var
		selection = self.listbox.curselection()
		if len(selection) == 0:
			self._selection = None
			view.disable()
			view.clear()
		else:
			name = self.listbox.get(selection[0])
			self._selection = name
			character_info = self._scenario.character_info(name)
			for i in info:
				s = None
				if i == 'name':
					s = name
				else:
					s = character_info[i]
				view.labelvars[i].set(s)
				view.editvars[i].set(s)
			view.enable()
	def _adapt_info(self):
		"""
		only called when loading
		"""
		self.save_memento(LoadAdaptdCharacterMemento(self, self._scenario))
	def add_character(self):
		if self._scenario is None:
			warn("add_character() fails: no scenario loaded.", UserWarning)
			return

		self.save_memento(NewCharacterMemento(self, self._scenario))
	def del_character(self, node):
		name = node.value.name
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

class CharacterEditorMemento(Memento):
	def __init__(self, editor, scenario):
		self._editor = editor
		self._scenario = scenario

class NewCharacterMemento(CharacterEditorMemento):
	def __init__(self, editor, scenario):
		super().__init__(editor, scenario)
		self.newname = None
	def execute(self):
		if self.newname is None:
			self.newname = self.name_generate()

		self._editor.listbox.insert('end', self.newname)
		self._scenario.create_character(self.newname, **self._editor.defaultinfo)
	def rollback(self):
		listbox = self._editor.listbox
		listbox.delete(listbox.size() - 1)

		self._scenario.delete_character(self.newname)
	def name_generate(self):
		for i in count(1):
			n = f'未命名{i}'
			if n not in self._scenario.character_names():
				return n

class LoadAdaptdCharacterMemento(BaseLoadAdaptMemento):
	def __init__(self, editor, scenario):
		self.editor = editor
		self.scenario = scenario
	def execute(self):
		for name in self.scenario.character.keys():
			info = self.scenario.character_info(name)
			self.expand_info(info)

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