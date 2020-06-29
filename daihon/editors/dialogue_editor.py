import tkinter as tk
import re
from enum import Flag, auto
from functools import partial, wraps
from operator import itemgetter
from tkinter import ttk, messagebox, simpledialog, scrolledtext

from .base import BaseEditor, BaseEditorView, BaseLoadAdaptMemento
from .memento import Memento

from ..scenario.base import ScenarioWithCharacters, ScenarioWithDialogue
from ..imageprocess.image_process_widget import ImageProcessFrame

delimiter = '：'
re_delimiter = re.compile('：|:')

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
		displaycolumns = tuple(sorted(c for c in columns if columns[c]['display_order'] is not None))
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
			self.tree.heading(c, text = c['text'])
	def _set_column_style(self, columns):
		self.tree.column('#0', **self.top_column['colstyle']) #special case
		for c in columns:
			if c.get('colstyle', None) is not None:
				self.tree.column(c, **c['colstyle'])
	def put_textedit_frame(self, frame):
		'''
		What input object is decided by controller
		We view just need to put it.
		'''
		#frame.grid(row = 0, column = 0, sticky = 'nsew')
		frame.pack()
	def build_selectall(self):
		frame = tk.Frame(self.edit_frame)

		select_all_button = tk.Button(frame)
		#self._select_all_var = tk.StringVar(frame)
		select_all_combobox = ttk.Combobox(frame, style = 'DialogueEditor.TCombobox')

		select_all_combobox.grid(row = 0, column = 0, sticky = 'nsew')
		select_all_button.grid(row = 0, column = 1, sticky = 'nsew')

		frame.pack()

		return select_all_button, select_all_combobox
	def build_buttons(self, groupname, info):
		frame = tk.Frame(self.edit_frame)

		for i, button in enumerate(info['buttons']):
			btn = tk.Button(frame, text = button['text'], command = button['command'], **button.get('style', {}))
			btn.grid(row = 0, column = i, sticky = 'nsew')
			button['button'] = btn
		frame.pack()

class DialogueEditor(BaseEditor):
	defaultinfo = {'text': '', 'speaker': ''}
	def _init_columns(self):
		self.columns = {
			"speaker": {
				'order': 0, #0-based
				'display_order': 0, #arbitrary based
				'text': '說話者',
				'default': '',
				'enable_state': _SelectState.select1 | _SelectState.select2,
			},
			"color": {
				'order': 1,
				'display_order': None, #not show
				'text': '顏色',
				'default': None,
			},
			"sentence": {
				'order': 2,
				'display_order': 1,
				'text': '台詞',
				'default': '',
				'colstyle': {'stretch': True, 'width': 500},
				'enable_state': _SelectState.select1,
			}
		}
		self.columns_default = [d['default'] for d in sorted(self.columns.values(), itemgetter('order'))]
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

		assert 'sentence' in self.columns
		sentence_edit_var = tk.StringVar(context_edit_frame)
		sentence_edit_entry = tk.Entry(context_edit_frame, textvariable = sentence_edit_var, width = 30)
		sentence_edit_label = tk.Label(context_edit_frame, textvariable = sentence_edit_var, width = 30)
		self.state_tran_register(sentence_edit_entry, self.columns['sentence']['enable_state'])
		sentence_edit_var.trace_add('write', lambda *args: self._modify_selected_info(sentence_edit_var, 'text', 'sentence'))

		speaker_edit_label.grid(row = 0, column = 0, sticky = 'nsew')
		speaker_edit_combobox.grid(row = 0, column = 1, sticky = 'nsew')
		sentence_edit_entry.grid(row = 0, column = 2, sticky = 'nsew')
		sentence_edit_label.grid(row = 1, column = 2, sticky = 'nsew')

		self.view.put_textedit_frame(context_edit_frame)

		self._speaker_edit_combobox = speaker_edit_combobox #fetch info

		self._speaker_edit_var = speaker_edit_var
		self._sentence_edit_var = sentence_edit_var
		self._sentence_edit_entry = sentence_edit_entry
		self._sentence_edit_label = sentence_edit_label
	def _init_selectall(self):
		btn, cbb = self.view.build_selectall()
		btn.config(text = '全選', command = self._select_all)
		cbb['values'] = ('(選擇角色以全選)', )
		cbb.current(0)
		cbb.state(['readonly'])

		self._select_all_combobox = cbb #fetch info
	def _init_buttons_info(self):
		self.buttons = {
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
						'text': '匯入台詞',
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
		self._decorate_button_command()
	def _install_buttons(self):
		for group in ('structural', 'merge', 'replace', 'image', 'test'):
			self.view.build_buttons(group, self.buttons[group])
			for button in self.buttons[group]:
				self.state_tran_register(button['button'], button['enable_state'])
	def _decorate_button_command(self):
		for d in self.buttons.values():
			for button in d['buttons']:
				button['command'] = self.condition_decorate(button['enable_state'], button['command'])
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

		self._init_selectall()

		self._init_buttons_info()
		self._install_buttons()

		#------------------
		self.tree = self.view.tree #for usual use

		self.tree.bind('<<TreeviewSelect>>', self._onselect)

		self._switch_edit_state()

		#self._sentence_edit_label['wraplength'] = self.winfo_width()

		self.bind('<Configure>', self._onresize)
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
	def _insert_text(self, mode = "END"):
		m = InsertSetenceMemento(self, self._scenario, mode)
		self.save_memento(m)
	def _replace_text(self, c):
		m = ReplaceTextMemento(self, self._scenario, c)
		self.save_memento(m)
	def _merge_text(self, mode, pad: str = ' '):
		try:
			m = MergeSetenceMemento(self, self._scenario, mode, pad)
		except:
			return
		self.save_memento(m)
	def _delete_selected_text(self):
		selection = self._selection
		if not messagebox.askokcancel('確認', f'即將刪除 {str(len(selection))} 個句子\n確定要刪除嗎？'):
			return
		m = DeleteSetenceMemento(self, self._scenario)
		self.save_memento(m)
	def _delete_text(self, *handlers):
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
		s = var.get()
		ori_d = {}
		for handler in self._selection:
			ori_d[handler] = self._scenario.dialogue[handler][key]
			self._modify_info(handler, (s, ), (key, ), (tree_key, ), (tag_change, ))
		self.save_memento(action = 'ModifySelectedInfo', detail = {'key': key, 'before': ori_d, 'after': s})
		'''
		if self._selection and len(self._selection) == 1:
			handler = self._selection[0]
			self._scenario.dialogue[handler][key] = var.get()
			if tree_key:
				self.tree.set(handler, tree_key, var.get())
			if tag_change:
				self.tree.item(handler, tags = var.get())
		'''
	def _modify_info(self, handler, contents, keys, tree_keys, tag_changes):
		for content, key, tree_key, tag_change in zip(contents, keys, tree_keys, tag_changes):
			self._scenario.dialogue[handler][key] = content
			if tree_key:
				self.tree.set(handler, tree_key, content)
			if tag_change:
				self.tree.item(handler, tags = (f'"{content}"', ))
	def _move_updown(self, up):
		m = MoveSetenceMemento(self, self._scenario, up)
		self.save_memento(m)
	def _select_all(self):
		i = self._select_all_combobox.current()
		if i == 0:
			self.tree.selection_set(*self.tree.get_children())
		else:
			h = f'"{self._select_all_combobox["value"][i]}"'
			self.tree.selection_set(*self.tree.tag_has(h))
	def _injure(self):
		ori_text = self._injure_encode()
		a = InjureTextDialog(self, '編輯台詞', ori_text).result
		if a is not None:
			self.save_memento(action = 'injure', detail = {'key': None, 'before': ori_text, 'after': a})
			self._injure_decode(a)
	def _injure_encode(self) -> str:
		l = []
		i_s, i_t = self.columns['speaker']['order'], self.columns['sentence']['order']
		for h in self.tree.get_children():
			v = self.tree.item(h)['values']
			print(v[i_t], v[i_s])
			#this is a problem when v[i_s] is a full-width number
			#I want a full-width number string, but it "automatically" turns it into an integer!
			s = v[i_t] if len(str(v[i_s])) == 0 else f'{v[i_s]}{delimiter}{v[i_t]}'
			l.append(s)
		return '\n'.join(l)
	def _injure_decode(self, s):
		l = s.split('\n')
		handlers = list(self.tree.get_children())
		diff = len(l) - len(handlers)
		if diff < 0:
			self._delete_text(*handlers[len(l):])
			handlers = handlers[:len(l)]
		elif diff > 0:
			for _ in range(diff):
				h = self._insert_text()
				handlers.append(h)
		for s, handler in zip(l, handlers):
			splits = re_delimiter.split(s, 1)
			if len(splits) == 1 or len(splits[0]) == 0:
				speaker, text = '', splits[-1]
			else:
				speaker, text = splits
			self._modify_info(handler, [speaker, text], ['speaker', 'text'], ['speaker', 'sentence'], [True, False])
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
			color = None
			if speaker in scenario.character:
				color = scenario.character[speaker]['color']
			sentence = info['text']
			self.tree.insert('', 'end', iid = handler, values = [speaker, color, sentence], tags = (f'"{speaker}"', ))
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
		self._select_all_combobox['value'] = ('(選擇角色以全選)', *l)
	def upload_to_scenario(self):
		#self.tree.selection_remove(*self.tree.selection())
		pass
	def _adapt_info(self):
		"""
		only called when loading
		"""
		changed = False
		for handler in self._scenario.handlers():
			info = self._scenario.sentence_info(handler)
			if self.expand_info(info) is True:
				changed = True
		if changed:
			self.save_memento(action = 'LoadAdapt', detail = {})

class InjureTextDialog(simpledialog.Dialog):
	def __init__(self, parent, title, text):
		self.init_text = text
		super().__init__(parent, title)
	def body(self, master):
		self._text = scrolledtext.ScrolledText(master)
		self._text.insert('end', self.init_text)
		self._text.pack()
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
			self.handlers = tuple(scenario.insert_sentence(**editor.defaultinfo) for _ in index)
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
		self._editor._delete_text(*self.handlers)
		if self.mode != 'END':
			self._editor.reorder_line_number()

class ReplaceTextMemento(DialogueEditorMemento):
	def __init__(self, editor, scenario, c):
		super().__init__(editor, scenario)
		self.handler = editor.selection[0]
		self.ori_text = scenario.dialogue[self.handler]['text']
		self.sol_text = self.ori_text.replace(' ', c, 1)
	def execute(self):
		self._editor._modify_info(self.handler, (self.sol_text, ), ('text', ), ('sentence', ), (False, ))
		self._editor.tree.selection_set(selection)
	def rollback(self):
		self._editor._modify_info(self.handler, (self.ori_text, ), ('text', ), ('sentence', ), (False, ))
		self._editor.tree.selection_set(selection)

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
		self.merged_text = scenario.dialogue[merged]['text']
		self._merged_info = self._grab_sentence_info(selection)
	def execute(self):
		merged, merge_into = self.merged, self.merge_into
		up = self.up
		base_text, selected_text = self.base_text, self.merged_text
		#key_info = ('up', pad, merge_into, selection) if up else ('down', pad, selection, merge_into)
		chain = (base_text, selected_text) if up else (selected_text, base_text)
		sol_text = self.pad.join(chain)
		self._editor._modify_info(merge_into, (sol_text, ), ('text', ), ('sentence', ), (False, ))

		self._editor.tree.selection_set(merge_into)
		self._editor._delete_text(selection)
		self._editor.reorder_line_number()
	def rollback(self):
		self._editor._modify_info(self.merge_into, (self.base_text, ), ('text', ), ('sentence', ), (False, ))
		self._restore_from_sentence_info(self.merged, self.merged_index, self._merged_info)
		self.scenario.set_sentence_order(self.merged, self.merged_index)

class DeleteSetenceMemento(DialogueEditorMemento):
	def __init__(self, editor, scenario):
		super().__init__(editor, scenario)
		self.handlers = {h: self._grab_sentence_info(h) for h in editor.selection}
		self.index = scenario.batch_get_sentence_order(editor.selection)
		self._handlers_order = sorted(zip(self.handlers, self.index), key = itemgetter(1))
	def execute(self):
		self._editor.tree.selection_remove(*self.handlers)
		self._editor._delete_text(*self.handlers)
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
	def __init__(self, editor, scenario, s):
		pass

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