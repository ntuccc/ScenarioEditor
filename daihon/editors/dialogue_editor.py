import tkinter as tk
import re
from copy import deepcopy
from enum import Flag, auto
from functools import partial, wraps
from operator import itemgetter
from tkinter import ttk, messagebox, simpledialog, scrolledtext

from .base import BaseEditor, BaseEditorView, BaseLoadAdaptMemento
from .memento import Memento

from ..scenario.base import ScenarioWithCharacters, ScenarioWithDialogue
from ..imageprocess.image_process_widget import ImageProcessFrame

class _SelectState(Flag):
	select0 = auto()
	select1 = auto()
	select2 = auto()
	always = select0 | select1 | select2
	noway = 0

class DialogueEditorView(BaseEditorView):
	top_column = {
		'text': '行號',
		'colstyle': {'anchor': tk.CENTER, 'stretch': True, 'width': 50}
	}
	def __init__(self, master, *args, **kwargs):
		super().__init__(master, *args, **kwargs, class_ = 'DialogueEditor')

		self._tree_frame = tk.Frame(self)
		self._tree_frame.pack(expand = True, fill = tk.BOTH)

		self.edit_frame = tk.Frame(self)
		#self.edit_frame.grid_rowconfigure(1, weight = 1)
		self.edit_frame.grid_columnconfigure(1, weight = 1)
		self.edit_frame.grid_columnconfigure(2, weight = 1, minsize = 300)

		self.edit_frame.pack(pady = 10, expand = True, fill = tk.X)
	def build_tree(self, columns):
		displaycolumns = tuple(sorted((c for c in columns if columns[c]['display_order'] is not None), key = lambda c: columns[c]['display_order']))
		self.tree = ttk.Treeview(self._tree_frame, columns = tuple(columns.keys()), displaycolumns = displaycolumns)
		self.tree.pack(side = tk.LEFT, expand = True, fill = tk.BOTH)

		sb = ttk.Scrollbar(self._tree_frame, orient = 'vertical', command = self.tree.yview)
		sb.pack(side = tk.RIGHT, fill = tk.Y)
		self.tree['yscrollcommand'] = sb.set

		self._set_headings(columns)
		self._set_column_style(columns)
	def _set_headings(self, columns):
		self.tree.heading('#0', text = self.top_column['text']) #special case
		for c in columns:
			self.tree.heading(c, text = columns[c]['text'])
	def _set_column_style(self, columns):
		self.tree.column('#0', **self.top_column['colstyle']) #special case
		for c in columns:
			if columns[c].get('colstyle', None) is not None:
				self.tree.column(c, **columns[c]['colstyle'])
	def put_textedit_frame(self, frame):
		'''
		What input object is decided by controller
		We view just need to put it.
		'''
		#frame.grid(row = 0, column = 0, sticky = 'nsew')
		frame.pack()
	def build_selectall(self):
		NotImplemented
	def build_buttons(self, groupname, info):
		frame = tk.Frame(self.edit_frame)

		for i, button in enumerate(info['buttons']):
			btn = tk.Button(frame, text = button['text'], command = button['command'], **button.get('style', {}))
			btn.grid(row = 0, column = i, sticky = 'nsew')
			button['button'] = btn
		frame.pack()

class DialogueEditor(BaseEditor):
	defaultinfo = {'text': '', 'speaker': '', 'speaker_list': []}
	def _init_columns(self):
		self.columns = {
			"speaker": {
				'order': 0, #0-based
				'display_order': 0, #arbitrary based
				'text': '顯示說話者',
				'default': '',
				'enable_state': _SelectState.select1 | _SelectState.select2,
			},
			"speaker_list": {
				'order': 1,
				'display_order': 1,
				'text': '說話者',
				'default': '',
				'enable_state': _SelectState.select1 | _SelectState.select2,
			},
			#"color": {
			#	'order': 2,
			#	'display_order': None, #not show
			#	'text': '顏色',
			#	'default': None,
			#},
			"sentence": {
				'order': 2,
				'display_order': 1,
				'text': '台詞',
				'default': '',
				'colstyle': {'stretch': True, 'width': 500},
				'enable_state': _SelectState.select1,
			}
		}
		self.columns_default = [d['default'] for d in sorted(self.columns.values(), key = itemgetter('order'))]
	def _init_textedit_frame(self):
		'''
		build content edit part along with columns information
		'''
		edit_frame = self.view.edit_frame
		context_edit_frame = tk.Frame(edit_frame)

		assert 'speaker' in self.columns
		speaker_edit_label = tk.Label(context_edit_frame, text = self.columns['speaker']['text'])
		speaker_edit_var = tk.StringVar(context_edit_frame)
		speaker_edit_combobox = ttk.Combobox(context_edit_frame, textvariable = speaker_edit_var, style = 'DialogueEditor.TCombobox')
		speaker_edit_combobox['values'] = ('')
		self.state_tran_register(speaker_edit_combobox, self.columns['speaker']['enable_state'])
		speaker_edit_var.trace_add('write', lambda *args: self._modify_selected_info(speaker_edit_var, 'speaker', 'speaker', tag_change = True))

		assert 'speaker_list' in self.columns
		speaker_list_command = self.condition_decorate(self.columns['speaker_list']['enable_state'], self._speaker_select)
		speaker_list_button = tk.Button(context_edit_frame, text = f"{self.columns['speaker_list']['text']}", command = speaker_list_command)
		self.state_tran_register(speaker_list_button, self.columns['speaker_list']['enable_state'])

		assert 'sentence' in self.columns
		sentence_edit_var = tk.StringVar(context_edit_frame)
		sentence_edit_entry = tk.Entry(context_edit_frame, textvariable = sentence_edit_var, width = 30)
		sentence_edit_label = tk.Label(context_edit_frame, textvariable = sentence_edit_var, width = 30)
		self.state_tran_register(sentence_edit_entry, self.columns['sentence']['enable_state'])
		sentence_edit_var.trace_add('write', lambda *args: self._modify_selected_info(sentence_edit_var, 'text', 'sentence'))

		speaker_edit_label.grid(row = 0, column = 0, sticky = 'nsew')
		speaker_edit_combobox.grid(row = 0, column = 1, sticky = 'nsew')
		speaker_list_button.grid(row = 0, column = 2, sticky = 'nsew')
		sentence_edit_entry.grid(row = 0, column = 3, sticky = 'nsew')
		sentence_edit_label.grid(row = 1, column = 3, sticky = 'nsew')

		self.view.put_textedit_frame(context_edit_frame)

		self._speaker_edit_combobox = speaker_edit_combobox #fetch info

		self._speaker_edit_var = speaker_edit_var
		self._sentence_edit_var = sentence_edit_var
		self._sentence_edit_entry = sentence_edit_entry
		self._sentence_edit_label = sentence_edit_label
	def _init_buttons_info(self):
		self.buttons = {
			'select': {
				'info': {},
				'buttons': [
					{
						'text': '選擇指定台詞',
						'command': self._select_all,
						'enable_state': _SelectState.always,
					}
				]
			},
			'structural': {
				'info': {},
				'buttons': [
					{
						'text': '上移',
						'command': partial(self._move_updown, up = True),
						'enable_state': _SelectState.select1 | _SelectState.select2,
					},
					{
						'text': '下移',
						'command': partial(self._move_updown, up = False),
						'enable_state': _SelectState.select1 | _SelectState.select2,
					},
					{
						'text': '向上新增',
						'command': partial(self._insert_text, 'up'),
						'enable_state': _SelectState.select1 | _SelectState.select2,
					},
					{
						'text': '向下新增',
						'command': partial(self._insert_text, 'down'),
						'enable_state': _SelectState.select1 | _SelectState.select2,
					},
					{
						'text': '新增於末尾',
						'command': self._insert_text,
						'enable_state': _SelectState.always,
					},
					{
						'text': '刪除',
						'command': self._delete_selected_text,
						'enable_state': _SelectState.select1 | _SelectState.select2,
						'style': {'fg': 'red'},
					},
				]
			},
			'merge': {
				'info': {},
				'buttons': [
					{
						'text': '向上合併',
						'command': partial(self._merge_text, 'up'),
						'enable_state': _SelectState.select1,
					},
					{
						'text': '向下合併',
						'command': partial(self._merge_text, 'down'),
						'enable_state': _SelectState.select1,
					},
				]
			},
			'replace': {
				'info': {},
				'buttons': [
					{
						'text': '←',
						'command': partial(self._replace_text, ''),
						'enable_state': _SelectState.select1,
					},
					{
						'text': '，',
						'command': partial(self._replace_text, '，'),
						'enable_state': _SelectState.select1,
					},
					{
						'text': '？',
						'command': partial(self._replace_text, '？'),
						'enable_state': _SelectState.select1,
					},
					{
						'text': '！',
						'command': partial(self._replace_text, '！'),
						'enable_state': _SelectState.select1,
					},
					{
						'text': '。',
						'command': partial(self._replace_text, '。'),
						'enable_state': _SelectState.select1,
					},
					{
						'text': '…',
						'command': partial(self._replace_text, '……'),
						'enable_state': _SelectState.select1,
					},
					{
						'text': '～',
						'command': partial(self._replace_text, '～'),
						'enable_state': _SelectState.select1,
					},
				]
			},
			'image': {
				'info': {},
				'buttons': [
					{
						'text': '置換台詞',
						'command': self._injure,
						'enable_state': _SelectState.always,
					},
					{
						'text': '辨識圖片',
						'command': self._image,
						'enable_state': _SelectState.always,
					},
				]
			},
			'test': {
				'info': {},
				'buttons': [
					{
						'text': 'test',
						'command': lambda: print(self._scenario.encode(indent = '\t')),
						'enable_state': _SelectState.always,
					},
				]
			},
		}
		for d in self.buttons.values():
			for button in d['buttons']:
				button['command'] = self.condition_decorate(button['enable_state'], button['command'])
	def _install_buttons(self):
		for group in ('select', 'structural', 'merge', 'replace', 'image'):
			self.view.build_buttons(group, self.buttons[group])
			for button in self.buttons[group]['buttons']:
				self.state_tran_register(button['button'], button['enable_state'])
	def __init__(self, master, *args, **kwargs):
		super().__init__(master, *args, viewClass = DialogueEditorView, **kwargs)

		self._selection = () #keep this variable is not to trigger the var.trace function
		self._state_trans_registration = []
		self._last_state = _SelectState.noway
		#self._listframe = tk.Frame(self)
		#self._listframe.pack()

		#------------------
		self._init_columns()
		self.view.build_tree(self.columns)

		self._init_textedit_frame()

		self._init_buttons_info()
		self._install_buttons()

		#------------------
		self.tree = self.view.tree #for usual use

		self.tree.bind('<<TreeviewSelect>>', self._onselect)

		self._switch_edit_state()

		#self._sentence_edit_label['wraplength'] = self.winfo_width()

		self.view.bind('<Configure>', self._onresize)
	@property
	def selection(self):
		return self._selection
	def destroy(self):
		self._selection = None
		super().destroy()
	def state_tran_register(self, obj, flag, special = None):
		'''
		special to specify what value to set instead of tk.NORMAL
		'''
		self._state_trans_registration.append((obj, flag, special))
	def get_state(self):
		try:
			if len(self._selection) == 0:
				return _SelectState.select0
			elif len(self._selection) == 1:
				return _SelectState.select1
			else:
				return _SelectState.select2
		except:
			return _SelectState.noway
	def condition_decorate(self, enable_state, f):
		@wraps(f)
		def g():
			if self.get_state() & enable_state:
				f()
		return g
	def _onselect(self, *args):
		if not self._scenario:
			return
		'''if len(selection) == 1:
			selection = selection[0]
			if self._selection == selection:
				return
		else:
			if self._selection is None:
				return
		'''
		#
		self._selection = None #do not trigger the trace of var
		selection = self.tree.selection()
		if len(selection) == 1:
			handler = selection[0]
			d = self._scenario.dialogue[handler]
			self._speaker_edit_var.set(d['speaker'])
			self._sentence_edit_var.set(d['text'])
		else:
			self._speaker_edit_var.set('')
			self._sentence_edit_var.set('')
		self._selection = selection
		self._switch_edit_state()
		print(selection)
	def _onresize(self, e = None):
		self._sentence_edit_label['wraplength'] = self._sentence_edit_entry.winfo_width()
	def _speaker_select(self):
		selection = self._selection

		speaker_list = None
		for handler in selection:
			if speaker_list is None:
				speaker_list = set(self._scenario.dialogue[handler]['speaker_list'])
			elif speaker_list != set(self._scenario.dialogue[handler]['speaker_list']):
				speaker_list = None
				break

		a = SpeakerListDialog(self, self._scenario, speaker_list, '選擇說話者').result
		if a is not None:
			self.save_memento(ModifyInfoMemento(self, self._scenario, self._selection, a, 'speaker_list', 'speaker_list', False))
	def _insert_text(self, mode = "END"):
		m = InsertSetenceMemento(self, self._scenario, mode)
		self.save_memento(m)
	def _replace_text(self, c):
		m = ReplaceTextMemento(self, self._scenario, c)
		self.save_memento(m)
	def _merge_text(self, mode, pad: str = ' '):
		try:
			m = MergeSetenceMemento(self, self._scenario, mode, pad)
		except Exception as e:
			print(e)
			return
		self.save_memento(m)
	def _delete_selected_text(self):
		selection = self._selection
		if not messagebox.askokcancel('確認', f'即將刪除 {len(selection)} 個句子\n確定要刪除嗎？'):
			return
		m = DeleteSetenceMemento(self, self._scenario)
		self.save_memento(m)
	def delete_text(self, handlers):
		self._scenario.delete_sentence(*handlers)
		self.tree.delete(*handlers)
	def reorder_line_number(self):
		'''
		used to refresh ALL sentence's order
		'''
		for number, h in enumerate(self.tree.get_children(), 1):
			self.tree.item(h, text = str(number))
	def _switch_edit_state(self):
		state = self.get_state()
		if state is self._last_state:
			return
		for obj, s, special in self._state_trans_registration:
			if s & state:
				#special is unused so far
				obj['state'] = tk.NORMAL
			else:
				obj['state'] = tk.DISABLED

		self._last_state = state
	def _modify_selected_info(self, var, key, tree_key, tag_change = False):
		if self._selection is None:
			return
		s = var.get()
		m = ModifyInfoMemento(self, self._scenario, self._selection, s, key, tree_key, tag_change)
		self.save_memento(m)
	def modify_info(self, handler, contents, keys, tree_keys, tag_changes):
		for content, key, tree_key, tag_change in zip(contents, keys, tree_keys, tag_changes):
			self._scenario.dialogue[handler][key] = content
			content_str = self.obj_to_str(content)
			if tree_key:
				self.tree.set(handler, tree_key, content_str)
			if tag_change:
				self.tree.item(handler, tags = (f'"{content_str}"', ))
	def obj_to_str(self, obj):
		if isinstance(obj, str):
			return obj
		if isinstance(obj, list):
			return '/'.join(self.obj_to_str(i) for i in obj)
		if isinstance(obj, dict):
			NotImplemented
		return str(obj)
	def _move_updown(self, up):
		m = MoveSetenceMemento(self, self._scenario, up)
		self.save_memento(m)
	def _select_all(self):
		a = SelectAllDialog(self, self._scenario, '選擇').result
		if a is not None:
			self.tree.selection_set(*a)
	def _injure(self):
		#ori_text = InjureSetenceMemento.injure_encode(self)
		#a = InjureTextDialog(self, '編輯台詞', ori_text).result
		a = InjureTextDialog(self.view, '置換台詞').result
		if a is not None:
			m = InjureSetenceMemento(self, self._scenario, a, '：|:')
			self.save_memento(m)
	def _image(self):
		ImageProcessDialog(self)
	def load_scenario(self, scenario):
		self.tree.delete(*self.tree.get_children())

		self._scenario = scenario
		self._onselect()
		dialogue = scenario.dialogue
		self._adapt_info()

		for i, handler in enumerate(scenario.handlers()):
			info = scenario.dialogue[handler]
			speaker = info['speaker']
			#color = None
			#if speaker in scenario.character:
			#	color = scenario.character[speaker]['color']
			speaker_list_str = '/'.join(info['speaker_list'])
			sentence = info['text']
			self.tree.insert('', 'end', iid = handler, values = [speaker, speaker_list_str, sentence], tags = (f'"{speaker}"', ))
		self.reorder_line_number()
		self.fetch_character_info([])
	def _grab_character_order(self):
		d, l = {}, []
		for name in self._scenario.character_names():
			try:
				d[name] = self._scenario.character[name]['order']
			except KeyError:
				l.append(name)
		return sorted(d.keys(), key = lambda n: d[n]) + l
	def fetch_character_info(self, changes: list = None):
		l = self._grab_character_order()
		self._speaker_edit_combobox['value'] = ('', *l)
	def upload_to_scenario(self):
		#self.tree.selection_remove(*self.tree.selection())
		pass
	def _adapt_info(self):
		"""
		only called when loading
		"""
		self.save_memento(LoadAdaptdDialogueMemento(self, self._scenario))

class SpeakerListDialog(simpledialog.Dialog):
	def __init__(self, editor, scenario, speaker_list, title):
		self.editor = editor
		self.characters = [character for character in scenario.character]
		self._ori_list = speaker_list
		super().__init__(editor.view, title)
	def body(self, master):
		label = tk.Label(self, text = '選擇角色')
		label.pack()

		frame = tk.Frame(self)

		scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
		self._listbox = tk.Listbox(frame, selectmode = tk.EXTENDED, yscrollcommand=scrollbar.set, activestyle = tk.NONE, exportselection = False)
		scrollbar.config(command=self._listbox.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		self._listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		for character in self.characters:
			self._listbox.insert('end', character)

		frame.pack()

		if self._ori_list is not None:
			for i in self._ori_list:
				self._listbox.selection_set(i)
	def buttonbox(self):
		box = tk.Frame(self)

		w = tk.Button(box, text = "確認", command=self.ok)
		w.pack(side = tk.LEFT, padx = 5, pady = 5)
		w = tk.Button(box, text="取消", command=self.cancel)
		w.pack(side = tk.LEFT, padx = 5, pady = 5)

		box.pack()
	def apply(self):
		self.result = [self.characters[i] for i in self._listbox.curselection()]

class SelectAllDialog(simpledialog.Dialog):
	def __init__(self, editor, scenario, title):
		self.editor = editor
		self.scenario = scenario
		super().__init__(editor.view, title)
	def body(self, master):
		frame = tk.Frame(self)

		label = tk.Label(frame, text = '顯示說話者名稱')
		self.entry_var = tk.StringVar(frame)
		entry = tk.Entry(frame, textvariable = self.entry_var)
		label.grid(row = 0, column = 0)
		entry.grid(row = 0, column = 1)

		frame.pack()
	def buttonbox(self):
		box = tk.Frame(self)

		w = tk.Button(box, text = "確認", command=self.ok)
		w.pack(side = tk.LEFT, padx = 5, pady = 5)
		w = tk.Button(box, text="取消", command=self.cancel)
		w.pack(side = tk.LEFT, padx = 5, pady = 5)

		box.pack()
	def apply(self):
		s = self.entry_var.get()
		scenario = self.scenario
		self.result = [h for h in scenario.handlers() if scenario.dialogue[h]['speaker'] == s]

class InjureTextDialog(simpledialog.Dialog):
	def __init__(self, parent, title, text = ''):
		self.init_text = text
		super().__init__(parent, title)
	def body(self, master):
		self._text = scrolledtext.ScrolledText(master)
		self._text.insert('end', self.init_text)
		self._text.pack()

		label = tk.Label(self, text = '注意！按下確定即會將原本內容全部替換', fg = 'red')
		label.pack()
	def buttonbox(self):
		box = tk.Frame(self)

		w = tk.Button(box, text = "確認", command=self.ok)
		w.pack(side = tk.LEFT, padx = 5, pady = 5)
		w = tk.Button(box, text="取消", command=self.cancel)
		w.pack(side = tk.LEFT, padx = 5, pady = 5)

		box.pack()
	def apply(self):
		self.result = self._text.get('1.0', 'end -1 chars')

class ImageProcessDialog(simpledialog.Dialog):
	def body(self, master):
		widget = ImageProcessFrame(self)
		widget.pack(expand = True, fill = tk.BOTH)
	def buttonbox(self):
		pass

class DialogueEditorMemento(Memento):
	def __init__(self, editor, scenario):
		self._editor = editor
		self._scenario = scenario
	def _grab_sentence_info(self, handler):
		return {'dialogue': self._scenario.dialogue[handler], 'tree': {info: self._editor.tree.item(handler)[info] for info in ('values', 'tags')}}
	def _restore_from_sentence_info(self, handler, index, info):
		#should called from up to down
		self._scenario.insert_sentence(predefined_handler = handler, **info['dialogue'])
		self._editor.tree.insert('', index, iid = handler, **info['tree'])

class ModifyInfoMemento(DialogueEditorMemento):
	def __init__(self, editor, scenario, selection, s, key, tree_key, tag_change):
		super().__init__(editor, scenario)

		self.selection = selection
		self.new_content = s
		self.key = key
		self.tree_key = tree_key
		self.tag_change = tag_change
		self.ori_content = {handler: scenario.dialogue[handler][key] for handler in selection}
	def execute(self):
		for handler in self.selection:
			self._editor.modify_info(handler, (self.new_content, ), (self.key, ), (self.tree_key, ), (self.tag_change, ))
	def rollback(self):
		for handler in self.selection:
			self._editor.modify_info(handler, (self.ori_content[handler], ), (self.key, ), (self.tree_key, ), (self.tag_change, ))

class InsertSetenceMemento(DialogueEditorMemento):
	def __init__(self, editor, scenario, mode):
		assert mode in ('END', 'up', 'down'), f'Wrong mode in {self.__class__}'
		super().__init__(editor, scenario)
		self.mode = mode
		self.handlers = None

		self.index = self._compute_index()
	def _compute_index(self):
		if self.mode == 'END':
			return (len(self._scenario.dialogue), )
		else:
			selection = self._editor.selection
			index = sorted(self._scenario.batch_get_sentence_order(selection))
			if self.mode == 'up':
				return tuple(i + j for j, i in enumerate(index))
			else:
				return tuple(i + j + 1 for j, i in enumerate(index))
	def execute(self):
		mode = self.mode
		editor = self._editor
		scenario = self._scenario
		index = self.index

		if self.handlers is None:
			self.handlers = self.new_sentence(len(index), scenario, editor.defaultinfo)
		else:
			for h in self.handlers:
				scenario.insert_sentence(predefined_handler = h, **editor.defaultinfo)

		#index is sorted
		for h, i in zip(self.handlers, index):
			if mode == 'END': #optimize for END
				editor.tree.insert('', 'end', iid = h, text = str(len(scenario.dialogue)), values = editor.columns_default, tags = '')
			else:
				editor.tree.insert('', i, iid = h, values = editor.columns_default, tags = '')

		if mode == 'END':
			#no need to set order
			pass
		if mode != 'END':
			scenario.batch_set_sentence_order(self.handlers, index)
			editor.reorder_line_number()
	def rollback(self):
		self._editor.tree.selection_remove(*self.handlers)
		self._editor.delete_text(self.handlers)
		if self.mode != 'END':
			self._editor.reorder_line_number()
	@staticmethod
	def new_sentence(n, scenario, defaultinfo, predefined_handlers = None):
		'''
		Provided API to insert n sentences into the scenario at the end
		'''
		if predefined_handlers is None:
			return tuple(scenario.insert_sentence(**defaultinfo) for _ in range(n))
		else:
			return tuple(scenario.insert_sentence(predefined_handler = h, **defaultinfo) for _, h in zip(range(n), predefined_handlers))

class ReplaceTextMemento(DialogueEditorMemento):
	def __init__(self, editor, scenario, c):
		super().__init__(editor, scenario)
		self.handler = editor.selection[0]
		self.ori_text = scenario.dialogue[self.handler]['text']
		self.sol_text = self.ori_text.replace(' ', c, 1)
	def execute(self):
		self._editor.modify_info(self.handler, (self.sol_text, ), ('text', ), ('sentence', ), (False, ))
		self._editor.tree.selection_set(self.handler)
	def rollback(self):
		self._editor.modify_info(self.handler, (self.ori_text, ), ('text', ), ('sentence', ), (False, ))
		self._editor.tree.selection_set(self.handler)

class MergeSetenceMemento(DialogueEditorMemento):
	def __init__(self, editor, scenario, mode, pad):
		super().__init__(editor, scenario)
		up = (mode == 'up')
		selection = editor.selection[0]
		index = editor.tree.index(selection)
		if (up and index == 0) or ((not up) and index == len(scenario.dialogue) - 1):
			#marginal condition
			raise ValueError('Not valid merge')
		merge_into_index = index - 1 if up else index + 1
		merge_into = editor.tree.get_children()[merge_into_index]

		self.up: bool = up
		self.pad = pad
		self.merged = selection
		self.merged_index = index
		self.merge_into = merge_into
		self.base_text = scenario.dialogue[merge_into]['text']
		self.merged_text = scenario.dialogue[self.merged]['text']
		self._merged_info = self._grab_sentence_info(selection)
	def execute(self):
		merged, merge_into = self.merged, self.merge_into
		up = self.up
		base_text, selected_text = self.base_text, self.merged_text
		#key_info = ('up', pad, merge_into, selection) if up else ('down', pad, selection, merge_into)
		chain = (base_text, selected_text) if up else (selected_text, base_text)
		sol_text = self.pad.join(chain)
		self._editor.modify_info(merge_into, (sol_text, ), ('text', ), ('sentence', ), (False, ))

		self._editor.tree.selection_set(merge_into)
		self._editor.delete_text([merged])
		self._editor.reorder_line_number()
	def rollback(self):
		self._editor.modify_info(self.merge_into, (self.base_text, ), ('text', ), ('sentence', ), (False, ))
		self._restore_from_sentence_info(self.merged, self.merged_index, self._merged_info)
		self._scenario.set_sentence_order(self.merged, self.merged_index)

class DeleteSetenceMemento(DialogueEditorMemento):
	def __init__(self, editor, scenario):
		super().__init__(editor, scenario)
		self.handlers = {h: self._grab_sentence_info(h) for h in editor.selection}
		self.index = scenario.batch_get_sentence_order(editor.selection)
		self._handlers_order = sorted(zip(self.handlers, self.index), key = itemgetter(1))
	def execute(self):
		self._editor.tree.selection_remove(*self.handlers)
		self._editor.delete_text(self.handlers)
		self._editor.reorder_line_number()
	def rollback(self):
		for h, i in self._handlers_order:
			#restore from up to down
			self._restore_from_sentence_info(h, i, self.handlers[h])
		self._scenario.batch_set_sentence_order(self.handlers.keys(), self.index)
		self._editor.reorder_line_number()

class MoveSetenceMemento(DialogueEditorMemento):
	def __init__(self, editor, scenario, up):
		super().__init__(editor, scenario)
		self.up = up
		self.handlers = editor.selection
		self._moved = None
	def execute(self):
		self._move(self.up)
	def rollback(self):
		self._move(not self.up)
	def _move(self, up):
		tree = self._editor.tree
		if up:
			if self._moved is None:
				self._moved = self._scenario.batch_increment_sentence_order(self.handlers)
			else:
				self._scenario.batch_increment_sentence_order(self._moved)
		else:
			if self._moved is None:
				self._moved = self._scenario.batch_decrement_sentence_order(self.handlers)
			else:
				self._scenario.batch_decrement_sentence_order(self._moved)
		for h in self._moved:
			index = tree.index(h)
			h_replaced = tree.prev(h) if up else tree.next(h)
			index_after = index + (-1 if up else 1)
			print(tree.item(h))
			tree.item(h, text = str(index_after + 1))
			tree.item(h_replaced, text = str(index + 1))
			tree.move(h, '', index_after)

class InjureSetenceMemento(DialogueEditorMemento):
	def __init__(self, editor, scenario, s, split_pattern = None):
		super().__init__(editor, scenario)
		self._l = s.split('\n')
		self.diff = len(self._l) - len(scenario.dialogue)
		self._changed_handlers = None
		self._dialogue = deepcopy(scenario.dialogue)
		self._new_dialogue = None
		self._split = re.compile(split_pattern) if split_pattern is not None else None
	def execute(self):
		self._injure(self.diff, self._new_dialogue)
	def _injure(self, diff, dialogue):
		if diff < 0:
			self._changed_handlers = list(self._scenario.handlers())[-self.diff:]
			self._editor.tree.selection_remove(*self._changed_handlers)
			self._editor.delete_text(self._changed_handlers)
		elif diff > 0:
			ori_n = len(self._scenario.dialogue)
			self._changed_handlers = InsertSetenceMemento.new_sentence(self.diff, self._scenario, self._editor.defaultinfo)
			for i, h in enumerate(self._changed_handlers, 1):
				self._editor.tree.insert('', 'end', iid = h, text = str(ori_n + i), values = self._editor.columns_default, tags = '')

		#on first call
		if dialogue is None:
			self._new_dialogue = self.injure_decode(self._l)
			dialogue = self._new_dialogue

		for h in self._scenario.handlers():
			self._editor.modify_info(h, [dialogue[h]['speaker'], dialogue[h]['text']], ['speaker', 'text'], ['speaker', 'sentence'], [True, False])
	def injure_decode(self, l):
		if self._split is None:
			result = {h: {'speaker': '', 'text': s} for h, s in zip(self._scenario.handlers(), l)}
		else:
			result = {h: {
				'speaker': ('' if len(l := self._split.split(s, 1)) == 1 else l[0]),
				'text': (s if len(l) == 1 else l[1])} for h, s in zip(self._scenario.handlers(), l)}
		return result

class LoadAdaptdDialogueMemento(BaseLoadAdaptMemento):
	def __init__(self, editor, scenario):
		self.editor = editor
		self.scenario = scenario
	def execute(self):
		for handler in self.scenario.handlers():
			info = self.scenario.sentence_info(handler)
			self.editor.expand_info(info)

if __name__ == '__main__':
	from scenario import Scenario
	from tkinter import font
	t = tk.Tk()
	#t.grid_rowconfigure(0, weight=1)
	#t.grid_columnconfigure(0, weight=1)
	#f = font.nametofont("TkDefaultFont")
	f = font.Font(t, family = "微軟正黑體", size = 12)
	t.option_add("*font", f)
	#rowheight should be set everytime
	ttk.Style().configure("DialogueEditor.Treeview", font = f, rowheight = f.metrics('linespace')+2)
	d = DialogueEditor(t)
	d.pack(expand = True, fill = tk.BOTH)
	with open('test.json', encoding = 'utf-8') as file:
		s = Scenario.load(file)
	with open('basetest.json', encoding = 'utf-8') as file:
		s0 = Scenario.load(file)
	d.load_scenario(s)
	#d.load_scenario(s0)
	d.mainloop()