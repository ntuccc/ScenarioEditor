import tkinter as tk
import warnings
from functools import partial
from itertools import count
from tkinter import colorchooser, ttk, messagebox
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
		up_button = tk.Button(button_frame, text = '向上', command = up_command)
		down_button = tk.Button(button_frame, text = '向下', command = down_command)
		add_button.grid(row = 0, column = 0)
		del_button.grid(row = 0, column = 1, padx = 10)
		up_button.grid(row = 1, column = 0, pady = 10)
		down_button.grid(row = 1, column = 1)
		button_frame.pack()

		self._enable.append(del_button)
		self._enable.append(up_button)
		self._enable.append(down_button)
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

		self.view.build_list(self.add_character, self.del_character, partial(self.move_order, 'up'), partial(self.move_order, 'down'))
		self.view.build_modification(info, self.modify_info)
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
		self._adapt_order()
	def upload_to_scenario(self):
		"""
		The only place where order updates
		"""
		pass
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
	def _adapt_order(self):
		"""
		only called when loading
		"""
		self.save_memento(LoadAdaptdCharacterOrderMemento(self, self._scenario))
	def add_character(self):
		if self._scenario is None:
			warn("add_character() fails: no scenario loaded.", UserWarning)
			return

		self.save_memento(NewCharacterMemento(self, self._scenario))
	def del_character(self):
		if self._selection is None:
			return
		name = self._selection
		self.save_memento(DelCharacterMemento(self, self._scenario, name))
	def move_order(self, mode):
		if mode not in ('up', 'down'):
			return
		if self._selection is None:
			return
		name = self._selection
		order = self._scenario.character_info(name)['order']
		if mode == 'up' and order == 0:
			return
		if mode == 'down' and order == len(self._scenario.character) - 1:
			return
		self.save_memento(MoveCharacterMemento(self, self._scenario, name, mode))
	def modify_info(self):
		if self._selection is None:
			return
		name = self._selection
		view = self.view

		changed = False
		for i in info:
			if view.labelvars[i] != view.editvars[i]:
				changed = True
				break
		if not changed:
			return

		if view.labelvars['name'].get() != view.editvars['name'].get():
			if view.editvars['name'].get() in self._scenario.character:
				messagebox.showwarning(title = '警告', message = '因為重名，對名字的更改將不會提交')
				view.editvars['name'].set(view.labelvars['name'].get())

		self.save_memento(ModifyCharacterInfoMemento(self, self._scenario, name))
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
		self.neworder = None
	def execute(self):
		if self.newname is None:
			self.newname = self.name_generate()
			self.neworder = self._editor.listbox.size()

		self._editor.listbox.insert('end', self.newname)
		self._scenario.create_character(self.newname, **self._editor.defaultinfo)
		self._scenario.character_info(self.newname)['order'] = self.neworder
	def rollback(self):
		listbox = self._editor.listbox
		listbox.delete(listbox.size() - 1)

		self._scenario.delete_character(self.newname)
	def name_generate(self):
		for i in count(1):
			n = f'未命名{i}'
			if n not in self._scenario.character_names():
				return n

class DelCharacterMemento(CharacterEditorMemento):
	def __init__(self, editor, scenario, name):
		super().__init__(editor, scenario)
		self.name = name
		self.info = self._scenario.character_info(name)
	def execute(self):
		self._editor.listbox.delete(self.info['order'])
		self._scenario.delete_character(self.name)

		LoadAdaptdCharacterOrderMemento.refresh_order(self._editor.listbox, self._scenario)

		self._editor._onselect() #<<ListboxSelect>> is not raised automatically, so call explicitly
	def rollback(self):
		self._editor.listbox.insert(self.info['order'], self.name)
		self._scenario.create_character(self.name)
		self._scenario.character_info(self.name).update(self.info)

		LoadAdaptdCharacterOrderMemento.refresh_order(self._editor.listbox, self._scenario)

class ModifyCharacterInfoMemento(CharacterEditorMemento):
	def __init__(self, editor, scenario, name):
		super().__init__(editor, scenario)
		self.name = name
		self.info = scenario.character_info(name).copy()
		self.afterinfo = None
		self.aftername = None
	def execute(self):
		if self.afterinfo is None:
			self.afterinfo = self.info.copy()
			self.afterinfo.update({i: self._editor.view.editvars[i].get() for i in info if i != 'name'})

		self._scenario.character_info(self.name).update(self.afterinfo)

		if self.aftername is None:
			newname = self._editor.view.editvars['name'].get()
			if self.name == newname:
				self.aftername = False
			else:
				self.aftername = newname

		if self.aftername:
			# It is a coincidence to make the empty string not be a character name.
			# However, I still use False to indicate that it is really nothing to change.
			self.rename(self.name, self.aftername)

	def rollback(self):
		self._scenario.character_info(self.name).update(self.info)

		if self.aftername:
			self.rename(self.aftername, self.name)
	def rename(self, n1, n2):
		self._scenario.rename_character(n1, n2)
		listbox = self._editor.listbox
		order = self.info['order']
		listbox.delete(order)
		listbox.insert(order, n2)
		listbox.selection_set(order)
		self._editor._onselect() #<<ListboxSelect>> is not raised automatically, so call explicitly

class MoveCharacterMemento(CharacterEditorMemento):
	def __init__(self, editor, scenario, name, mode):
		super().__init__(editor, scenario)
		self.name = name
		self.mode = mode
		self.order = self._scenario.character_info(name)['order']
		self.target = None
	def execute(self):
		listbox = self._editor.listbox
		offset = -1 if self.mode == 'up' else +1
		if self.target is None:
			self.target = listbox.get(self.order + offset)

		self.move(offset)
	def rollback(self):
		self.move(+1 if self.mode == 'up' else -1)
	def move(self, offset):
		listbox = self._editor.listbox
		if self.target is None:
			self.target = listbox.get(self.order + offset)

		self._scenario.character_info(self.name)['order'] += offset
		self._scenario.character_info(self.target)['order'] -= offset

		listbox.delete(self.order + offset)
		listbox.insert(self.order + offset, self.name)
		listbox.delete(self.order)
		listbox.insert(self.order, self.target)

		listbox.selection_set(self.order + offset)

class LoadAdaptdCharacterMemento(BaseLoadAdaptMemento):
	def __init__(self, editor, scenario):
		self.editor = editor
		self.scenario = scenario
	def execute(self):
		for name in self.scenario.character.keys():
			info = self.scenario.character_info(name)
			self.expand_info(info)

class LoadAdaptdCharacterOrderMemento(BaseLoadAdaptMemento):
	def __init__(self, editor, scenario):
		self.editor = editor
		self.scenario = scenario
	@staticmethod
	def refresh_order(listbox, scenario):
		for i, name in enumerate(listbox.get(0, 'end')):
			scenario.character_info(name)['order'] = i
	def execute(self):
		self.refresh_order(self.editor.listbox, self.scenario)

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