import tkinter as tk
import warnings
from itertools import count
from tkinter import colorchooser, ttk
from typing import Optional
from warnings import warn

from .new_character_dialog import NewCharacterFrame
from .base import BaseEditor, EditorEvent

from ..ast.linkedlist import listnode, linkedlist
from ..scenario.base import ScenarioWithCharacters
from ..utils.scrollableframe import VerticalScrolledFrame

defaultcolor = '#ff0000'

additional_info = {
	'abbreviated': {'name': '簡稱', 'width': 5, 'default': ''},
	'gender': {'name': '性別', 'width': 5, 'default': '♀'},
	'cast': {'name': '聲優', 'width': 12, 'default': ''},
}

class CharacterFrame(tk.Frame):
	def __init__(self, character_info: dict, *args, name = '', **kwargs):
		grid_counter = count()
		super().__init__(*args, **kwargs, class_ = 'CharacterFrame')
		self._editor = self._grab_editor()

		self.listnode: Optional[listnode[CharacterFrame]] = None
		self._character_info = None
		self._tmpname: Optional[str] = None

		self._basedataframe = NewCharacterFrame(self)
		self._basedataframe.name = name
		self._basedataframe.grid(row = 0, column = next(grid_counter))

		self._basedataframe.name_entry.bind('<FocusIn>', self._namefocusin)
		self._basedataframe.name_entry.bind('<FocusOut>', self._namefocusout)
		self._basedataframe.color_var.trace_add('write', self._onchange('color', self._basedataframe.color_var))

		for n, d in additional_info.items():
			frame = tk.Frame(self)
			label = tk.Label(frame, text = d.get('name', ''))
			label.grid(row = 0, column = 0)
			string_var = tk.StringVar(frame)
			setattr(self, f'_{n}_var', string_var)
			entry = tk.Entry(frame, textvariable = string_var, width = d.get('width', 5))
			setattr(self, f'_{n}_entry', entry)
			entry.grid(row = 0, column = 1)
			entry.bind('<FocusOut>', self._onchange(n, string_var))

			frame.grid(row = 0, column = next(grid_counter), padx = 10)

		'''
		#abbreciated part
		abbreviated_frame = tk.Frame(self)
		abbreviated_label = tk.Label(abbreviated_frame, text = '簡稱')
		abbreviated_label.grid(row = 0, column = 0)
		self._abbreviated_var = tk.StringVar(abbreviated_frame)
		self._abbreviated_entry = tk.Entry(abbreviated_frame, textvariable = self._abbreviated_var, width = 5)
		self._abbreviated_entry.grid(row = 0, column = 1)

		#this one is inefficient
		#self._abbreviated_var.trace_add('write', self._onchange('abbreviated', self._abbreviated_var))
		self._abbreviated_entry.bind('<FocusOut>', self._onchange('abbreviated', self._abbreviated_var))

		abbreviated_frame.grid(row = 0, column = 1, padx = 10)

		#gender part
		gender_frame = tk.Frame(self)
		gender_label = tk.Label(gender_frame, text = '性別')
		gender_label.grid(row = 0, column = 0)
		self._gender_var = tk.StringVar(gender_frame)
		self._gender_entry = tk.Entry(gender_frame, textvariable = self._gender_var, width = 5)
		self._gender_entry.grid(row = 0, column = 1)

		gender_change_f = self._onchange('gender', self._gender_var)
		self._gender_entry.bind('<FocusOut>', gender_change_f)

		gender_frame.grid(row = 0, column = 2, padx = 10)
		'''

		if 'gender' in additional_info:
			gender_change_f = self._onchange('gender', self._gender_var)
			#gender change button
			gender_change_frame = tk.Frame(self)
			gender_to_boy = tk.Button(gender_change_frame, text = '男', command = (lambda: (self._gender_var.set('♂'), gender_change_f())))
			gender_to_girl = tk.Button(gender_change_frame, text = '女', command = (lambda: (self._gender_var.set('♀'), gender_change_f())))
			gender_to_boy.grid(row = 0, column = 0)
			gender_to_girl.grid(row = 0, column = 1)

			gender_change_frame.grid(row = 0, column = next(grid_counter), padx = 10)

		#order change button
		#order is post-updated. no Event fed
		order_change_frame = tk.Frame(self)
		order_increase = tk.Button(order_change_frame, text = '↑', command = (lambda: (self.namefocusin_check(), self._editor.move_order(self.listnode, 'up'))))
		order_decrease = tk.Button(order_change_frame, text = '↓', command = (lambda: (self.namefocusin_check(), self._editor.move_order(self.listnode, 'down'))))
		order_increase.grid(row = 0, column = 0)
		order_decrease.grid(row = 0, column = 1)

		order_change_frame.grid(row = 0, column = next(grid_counter), padx = 10)

		...

		#delete button
		delete_button = tk.Button(self, text = 'X', command = lambda: self._editor.del_character(self.listnode))
		delete_button.grid(row = 0, column = next(grid_counter), padx = 10)

		self.character_info_modify(character_info)
	def _onchange(self, info_key, var):
		def f(*_):
			if self._character_info:
				self.namefocusin_check()
				self._editor.save_memento(action = info_key, detail = {'key': self._tmpname or self.name, 'before': self._character_info[info_key], 'after': var.get()})
				self._character_info[info_key] = var.get()
		return f
	def _namefocusin(self, e):
		self._tmpname = self._basedataframe.name
	def namefocusin_check(self):
		if self._tmpname:
			name = self._basedataframe.name
			if len(name) >= 0 and self._editor.rename_character(self._tmpname, name):
				#rename success
				self._tmpname = name
	def _namefocusout(self, e):
		name = self._basedataframe.name
		if len(name) == 0 or not self._editor.rename_character(self._tmpname, name):
			#rename fail
			self._basedataframe.name = self._tmpname
		self._tmpname = None
	def _grab_editor(self):
		sol = self.master
		while not isinstance(sol, BaseEditor) and sol is not None:
			sol = sol.master
		return sol
	def destroy(self):
		del self._basedataframe
		del self._abbreviated_var
		del self._abbreviated_entry
		del self._gender_var
		del self._gender_entry
		self._character_info = None
		super().destroy()
	@property
	def name(self):
		return self._tmpname or self._basedataframe.name
	@name.setter
	def name(self, n):
		self._basedataframe.name = n
		if self._tmpname:
			self._tmpname = n
	def character_info_modify(self, character_info):
		self._character_info = None #simply prevent triggering the trace callback
		self._basedataframe.color = character_info['color']
		self._abbreviated_var.set(character_info['abbreviated'])
		self._gender_var.set(character_info['gender'])
		...
		self._character_info = character_info

class CharacterEditor(BaseEditor, VerticalScrolledFrame):
	defaultinfo = {n: d.get('default', '') for n, d in additional_info.items()}
	def __init__(self, master, *args, **kwargs):
		BaseEditor.__init__(self, master, *args, **kwargs, class_ = 'CharacterEditor')
		VerticalScrolledFrame.__init__(self, master, *args, **kwargs, class_ = 'CharacterEditor')
		self._charaframes_list: linkedlist[CharacterFrame] = linkedlist()

		self._listframe = tk.Frame(self.interior)
		self._listframe.pack()

		sep = ttk.Separator(self.interior, orient = 'horizontal')
		sep.pack(fill = tk.X, pady = 10)

		self._inputframe = tk.Frame(self.interior)
		self._inputframe.pack()

		self._newcharaframe = NewCharacterFrame(self._inputframe, defaultcolor = defaultcolor)
		self._newcharaframe.grid(row = 0, column = 0, padx = 10)

		newchara_button = tk.Button(self._inputframe, text = '增加角色', command = self.add_character)
		newchara_button.grid(row = 0, column = 1, padx = 10)

		test_button = tk.Button(self.interior, text = "test")
		test_button['command'] = lambda: print(self._scenario.encode(indent = '\t'))
		#test_button['command'] = lambda: (print(self._scenario.encode(indent = '\t')), print(repr(self._charaframes_list)))
		#test_button['command'] = lambda:(self._charaframes_list.head.value._basedataframe.name_entry.__setitem__('state', tk.DISABLED))
		#test_button['command'] = lambda: (self.upload_to_scenario(), print(self._scenario.encode(indent = '\t')))
		test_button.pack()
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

		#reuse of frame
		del_node = None
		for node in self._charaframes_list:
			if len(order) > 0:
				name = order[0]
				node.value.name = name
				node.value.character_info_modify(scenario.character_info(name))
				del order[0]
			else:
				del_node = node
				break
		if len(order) > 0:
			#create node
			for name in order:
				self._add_chara_tail(name, scenario.character_info(name))
		elif del_node:
			while del_node is not None:
				nextnode = del_node.next
				self.destroy_node(self._charaframes_list, del_node)
				del_node = nextnode
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
	def _add_chara_tail(self, name, character_info) -> CharacterFrame:
		newframe = CharacterFrame(master = self._listframe, name = name, character_info = character_info)
		#newframe.name = name
		newnode = listnode(value = newframe)
		newframe.listnode = newnode
		self._charaframes_list.append_tail(newnode)
		newframe.pack()
		return newframe
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