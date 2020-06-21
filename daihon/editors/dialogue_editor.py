import tkinter as tk
import re
from tkinter import ttk, messagebox, simpledialog, scrolledtext

from .base import BaseEditor, EditorEvent

from ..scenario.base import ScenarioWithCharacters, ScenarioWithDialogue
from ..imageprocess.image_process_widget import ImageProcessFrame

delimiter = '：'
re_delimiter = re.compile('：|:')

class DialogueEditor(BaseEditor):
	defaultinfo = {'text': '', 'speaker': ''}
	columns = {"speaker": 0, "color": 1, "sentence": 2}
	def __init__(self, master, *args, **kwargs):
		super().__init__(master, *args, **kwargs, class_ = 'DialogueEditor')

		self._selection = () #keep this variable is not to trigger the var.trace function
		#self._listframe = tk.Frame(self)
		#self._listframe.pack()
		tree_frame = tk.Frame(self)
		self._tree = ttk.Treeview(tree_frame, columns = tuple(self.columns.keys()), displaycolumns = ("speaker", "sentence"), style = 'DialogueEditor.Treeview')
		self._tree.pack(side = tk.LEFT, expand = True, fill = tk.BOTH)

		sb = ttk.Scrollbar(tree_frame, orient = 'vertical', command = self._tree.yview)
		sb.pack(side = tk.RIGHT, fill = tk.Y)
		self._tree['yscrollcommand'] = sb.set

		tree_frame.pack(expand = True, fill = tk.BOTH)

		self._tree.heading('#0', text = '行號')
		self._tree.heading('speaker', text = '說話者')
		self._tree.heading('color', text = '顏色')
		self._tree.heading('sentence', text = '台詞')

		self._tree.column('#0', anchor = tk.CENTER, stretch = True, width = 50)
		self._tree.column('sentence', stretch = True, width = 500)

		self._tree.bind('<<TreeviewSelect>>', self._onselect)

		edit_frame = tk.Frame(self)
		speaker_edit_label = tk.Label(edit_frame, text = '說話者')
		self._speaker_edit_var = tk.StringVar(edit_frame)
		self._speaker_edit_combobox = ttk.Combobox(edit_frame, textvariable = self._speaker_edit_var, style = 'DialogueEditor.TCombobox')
		self._speaker_edit_combobox['values'] = ('')
		self._text_edit_var = tk.StringVar(edit_frame)
		self._text_edit_entry = tk.Entry(edit_frame, textvariable = self._text_edit_var, width = 30)

		self._text_edit_label = tk.Label(edit_frame, textvariable = self._text_edit_var, width = 30)

		self._text_up_button = tk.Button(edit_frame, text = '上移', command = lambda: self._move_updown(up = True))
		self._text_down_button = tk.Button(edit_frame, text = '下移', command = lambda: self._move_updown(up = False))

		self._insert_up_button = tk.Button(edit_frame, text = '向上新增', command = lambda: self._insert_text('up'))
		self._insert_down_button = tk.Button(edit_frame, text = '向下新增', command = lambda: self._insert_text('down'))

		replace_frame = tk.Frame(edit_frame)

		self._replace_del = tk.Button(replace_frame, text = '←', command = lambda: self._replace_text(''))
		self._replace_comma = tk.Button(replace_frame, text = '，', command = lambda: self._replace_text('，'))
		self._replace_quest = tk.Button(replace_frame, text = '？', command = lambda: self._replace_text('？'))
		self._replace_surpr = tk.Button(replace_frame, text = '！', command = lambda: self._replace_text('！'))
		self._replace_end = tk.Button(replace_frame, text = '。', command = lambda: self._replace_text('。'))
		self._replace_dots = tk.Button(replace_frame, text = '…', command = lambda: self._replace_text('……'))
		self._replace_tilde = tk.Button(replace_frame, text = '～', command = lambda: self._replace_text('～'))

		self._replace_del.grid(row = 0, column = 0, sticky = "nsew")
		self._replace_comma.grid(row = 0, column = 1, sticky = "nsew")
		self._replace_quest.grid(row = 0, column = 2, sticky = "nsew")
		self._replace_surpr.grid(row = 0, column = 3, sticky = "nsew")
		self._replace_end.grid(row = 0, column = 4, sticky = "nsew")
		self._replace_dots.grid(row = 0, column = 5, sticky = "nsew")
		self._replace_tilde.grid(row = 0, column = 6, sticky = "nsew")

		self._merge_up_button = tk.Button(edit_frame, text = '向上合併', command = lambda: self._merge_text('up'))
		self._merge_down_button = tk.Button(edit_frame, text = '向下合併', command = lambda: self._merge_text('down'))

		insert_end_button = tk.Button(edit_frame, text = '新增於末尾', command = self._insert_text)

		self._delete_button = tk.Button(edit_frame, text = '刪除', fg = 'red', command = self._delete_selected_text)

		select_all_button = tk.Button(edit_frame, text = '全選', command = self._select_all)
		#self._select_all_var = tk.StringVar(edit_frame)
		self._select_all_combobox = ttk.Combobox(edit_frame, style = 'DialogueEditor.TCombobox')
		self._select_all_combobox['values'] = ('(選擇角色以全選)')
		self._select_all_combobox.current(0)

		speaker_edit_label.grid(row = 0, column = 0, sticky = "nsew")
		self._speaker_edit_combobox.grid(row = 0, column = 1, sticky = "nsew")
		self._text_edit_entry.grid(row = 0, column = 2, sticky = "nsew")
		self._text_up_button.grid(row = 0, column = 3, sticky = "nsew")
		self._text_down_button.grid(row = 0, column = 4, sticky = "nsew")
		self._insert_up_button.grid(row = 0, column = 5, sticky = "nsew")
		self._insert_down_button.grid(row = 0, column = 6, sticky = "nsew")
		replace_frame.grid(row = 1, column = 2, sticky = "nsew")
		self._merge_up_button.grid(row = 1, column = 5, sticky = "nsew")
		self._merge_down_button.grid(row = 1, column = 6, sticky = "nsew")
		insert_end_button.grid(row = 0, column = 7, sticky = "nsew")
		self._delete_button.grid(row = 0, column = 8, sticky = "nsew")
		select_all_button.grid(row = 2, column = 0, sticky = "nsew")
		self._select_all_combobox.grid(row = 2, column = 1, sticky = "nsew")
		self._text_edit_label.grid(row = 2, column = 2, sticky = "nsew")

		#edit_frame.grid_rowconfigure(1, weight = 1)
		edit_frame.grid_columnconfigure(1, weight = 1)
		edit_frame.grid_columnconfigure(2, weight = 1, minsize = 300)

		edit_frame.pack(pady = 10, expand = True, fill = tk.X)

		import_frame = tk.Frame(self)
		import_text_button = tk.Button(import_frame, text = '匯入台詞', command = self._injure)
		import_image_button = tk.Button(import_frame, text = '辨識圖片', command = self._image)

		import_text_button.grid(row = 0, column = 0)
		import_image_button.grid(row = 0, column = 1)

		import_frame.pack(padx = 10, expand = True)

		test_button = tk.Button(self, text = "test")
		test_button['command'] = lambda: print(self._scenario.encode(indent = '\t'))
		#test_button['command'] = lambda: self._tree.tag_configure('123', background = '#ff0000')
		#test_button['command'] = lambda: print(self._tree.tag_has('wayne'))
		#test_button['command'] = lambda: self._tree.delete(*self._tree.get_children())
		test_button.pack(expand = True, fill = tk.X)

		self._switch_edit_state(0)

		#self._text_edit_label['wraplength'] = self.winfo_width()

		self._select_all_combobox.state(['readonly'])

		self._speaker_edit_var.trace_add('write', lambda *args: self._modify_selected_info(self._speaker_edit_var, 'speaker', 'speaker', tag_change = True))
		self._text_edit_var.trace_add('write', lambda *args: self._modify_selected_info(self._text_edit_var, 'text', 'sentence'))
		self.bind('<Configure>', self._onresize)
	def destroy(self):
		self._selection = None
		super().destroy()
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
		self._selection = None
		selection = self._tree.selection()
		self._switch_edit_state(len(selection))
		if len(selection) == 1:
			handler = selection[0]
			d = self._scenario.dialogue[handler]
			self._speaker_edit_var.set(d['speaker'])
			self._text_edit_var.set(d['text'])
		else:
			self._speaker_edit_var.set('')
			self._text_edit_var.set('')
		self._selection = selection
		print(selection)
	def _onresize(self, e = None):
		self._text_edit_label['wraplength'] = self._text_edit_entry.winfo_width()
	def _insert_text(self, mode = "END"):
		if mode == 'END':
			h = self._scenario.insert_sentence(**self.defaultinfo)
			self._tree.insert('', 'end', iid = h, text = str(len(self._scenario.dialogue)), values = ['', None, ''], tags = '')
			self.save_memento(action = 'NewSentence', detail = {'key': h, 'before': None, 'after': None})
			return h
		else:
			if len(self._selection) == 0 or (mode != 'up' and mode != 'down'):
				return
			up = (mode == 'up')
			ite = iter(self._selection) if up else reversed(self._selection)
			ite_l = list(ite)
			newh_l = []
			for h in ite_l:
				newh = self._scenario.insert_sentence(**self.defaultinfo)
				newh_l.append(newh)
				ori_index = self._tree.index(h)
				new_index = (ori_index + 0) if up else (ori_index + 1)
				self._scenario.set_sentence_order(newh, new_index) #!!!this is O(n) operation!!!
				self._tree.insert('',  new_index, iid = newh, values = ['', None, ''], tags = '')
			self._reorder_line_number()
			self.save_memento(action = f'NewSentenceBatch{mode}', detail = {'key': newh_l, 'before': ite_l, 'after': None})
	def _replace_text(self, c):
		if len(self._selection) != 1:
			return
		selection = self._selection[0]
		text = self._scenario.dialogue[selection]['text']
		sol_text = text.replace(' ', c, 1)
		self._modify_info(selection, (sol_text, ), ('text', ), ('sentence', ), (False, ))
		self._tree.selection_set(selection)
		self.save_memento(action = 'ReplaceSpace', detail = {'key': c, 'before': text, 'after': sol_text})
	def _merge_text(self, mode, pad: str = ' '):
		if len(self._selection) != 1:
			return
		up = (mode == 'up')
		selection = self._selection[0]
		index = self._tree.index(selection)
		if (up and index == 0) or ((not up) and index == len(self._tree.get_children()) - 1):
			#marginal condition
			return
		merge_into_index = index - 1 if up else index + 1
		merge_into = self._tree.get_children()[merge_into_index]

		base_text, selected_text = self._scenario.dialogue[merge_into]['text'], self._scenario.dialogue[selection]['text']
		key_info = ('up', pad, merge_into, selection) if up else ('down', pad, selection, merge_into)
		before_info = (base_text, selected_text) if up else (selected_text, base_text)
		sol_text = pad.join(before_info)
		self._modify_info(merge_into, (sol_text, ), ('text', ), ('sentence', ), (False, ))

		self._tree.selection_set(merge_into)
		self._delete_text(selection)
		self._reorder_line_number()
		self.save_memento(action = 'MergeSentence', detail = {'key': key_info, 'before': before_info, 'after': sol_text})
	def _delete_selected_text(self):
		selection = self._selection
		if len(selection) == 0:
			return
		if not messagebox.askokcancel('確認', f'即將刪除 {str(len(selection))} 個句子\n確定要刪除嗎？'):
			return
		self.save_memento(action = 'DeleteSentence', detail = {'key': selection, 'before': [self._tree.index(s) for s in selection], 'after': None})
		self._tree.selection_remove(*selection)
		self._delete_text(*selection)
		self._reorder_line_number()
	def _delete_text(self, *handlers):
		self._scenario.delete_sentence(*handlers)
		self._tree.delete(*handlers)
	def _reorder_line_number(self):
		'''
		used to refresh ALL sentence's order
		'''
		for number, h in enumerate(self._tree.get_children(), 1):
			self._tree.item(h, text = str(number))
	def _switch_edit_state(self, n):
		if n == 0:
			self._speaker_edit_combobox['state'] = tk.DISABLED
			self._text_edit_entry['state'] = tk.DISABLED
			self._text_up_button['state'] = tk.DISABLED
			self._text_down_button['state'] = tk.DISABLED
			self._insert_up_button['state'] = tk.DISABLED
			self._insert_down_button['state'] = tk.DISABLED
			self._merge_up_button['state'] = tk.DISABLED
			self._merge_down_button['state'] = tk.DISABLED
			self._delete_button['state'] = tk.DISABLED
			self._replace_del['state'] = tk.DISABLED
			self._replace_comma['state'] = tk.DISABLED
			self._replace_quest['state'] = tk.DISABLED
			self._replace_surpr['state'] = tk.DISABLED
			self._replace_end['state'] = tk.DISABLED
			self._replace_dots['state'] = tk.DISABLED
			self._replace_tilde['state'] = tk.DISABLED
		elif n == 1:
			self._speaker_edit_combobox['state'] = tk.NORMAL
			self._text_edit_entry['state'] = tk.NORMAL
			self._text_up_button['state'] = tk.NORMAL
			self._text_down_button['state'] = tk.NORMAL
			self._insert_up_button['state'] = tk.NORMAL
			self._insert_down_button['state'] = tk.NORMAL
			self._merge_up_button['state'] = tk.NORMAL
			self._merge_down_button['state'] = tk.NORMAL
			self._delete_button['state'] = tk.NORMAL
			self._replace_del['state'] = tk.NORMAL
			self._replace_comma['state'] = tk.NORMAL
			self._replace_quest['state'] = tk.NORMAL
			self._replace_surpr['state'] = tk.NORMAL
			self._replace_end['state'] = tk.NORMAL
			self._replace_dots['state'] = tk.NORMAL
			self._replace_tilde['state'] = tk.NORMAL
		else:
			self._speaker_edit_combobox['state'] = tk.NORMAL
			self._text_edit_entry['state'] = tk.DISABLED
			self._text_up_button['state'] = tk.NORMAL
			self._text_down_button['state'] = tk.NORMAL
			self._insert_up_button['state'] = tk.NORMAL
			self._insert_down_button['state'] = tk.NORMAL
			self._merge_up_button['state'] = tk.DISABLED
			self._merge_down_button['state'] = tk.DISABLED
			self._delete_button['state'] = tk.NORMAL
			self._replace_del['state'] = tk.DISABLED
			self._replace_comma['state'] = tk.DISABLED
			self._replace_quest['state'] = tk.DISABLED
			self._replace_surpr['state'] = tk.DISABLED
			self._replace_end['state'] = tk.DISABLED
			self._replace_dots['state'] = tk.DISABLED
			self._replace_tilde['state'] = tk.DISABLED
	def _modify_selected_info(self, var, key, tree_key, tag_change = False):
		if not self._selection:
			return
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
				self._tree.set(handler, tree_key, var.get())
			if tag_change:
				self._tree.item(handler, tags = var.get())
		'''
	def _modify_info(self, handler, contents, keys, tree_keys, tag_changes):
		for content, key, tree_key, tag_change in zip(contents, keys, tree_keys, tag_changes):
			self._scenario.dialogue[handler][key] = content
			if tree_key:
				self._tree.set(handler, tree_key, content)
			if tag_change:
				self._tree.item(handler, tags = (f'"{content}"', ))
	def _move_updown(self, up):
		if up:
			l = self._scenario.batch_increment_sentence_order(self._selection)
		else:
			l = self._scenario.batch_decrement_sentence_order(self._selection)
		self.save_memento(action = 'MoveSentence', detail = {'key': l, 'before': None, 'after': 'up' if up else 'down'})
		for h in l:
			index = self._tree.index(h)
			h_replaced = self._tree.prev(h) if up else self._tree.next(h)
			index_after = index + (-1 if up else 1)
			print(self._tree.item(h))
			self._tree.item(h, text = str(index_after + 1))
			self._tree.item(h_replaced, text = str(index + 1))
			self._tree.move(h, '', index_after)
	def _select_all(self):
		i = self._select_all_combobox.current()
		if i == 0:
			self._tree.selection_set(*self._tree.get_children())
		else:
			h = f'"{self._select_all_combobox["value"][i]}"'
			self._tree.selection_set(*self._tree.tag_has(h))
	def _injure(self):
		ori_text = self._injure_encode()
		a = InjureTextDialog(self, '編輯台詞', ori_text).result
		if a is not None:
			self.save_memento(action = 'injure', detail = {'key': None, 'before': ori_text, 'after': a})
			self._injure_decode(a)
	def _injure_encode(self) -> str:
		l = []
		i_s, i_t = self.columns['speaker'], self.columns['sentence']
		for h in self._tree.get_children():
			v = self._tree.item(h)['values']
			print(v[i_t], v[i_s])
			#this is a problem when v[i_s] is a full-width number
			#I want a full-width number string, but it "automatically" turns it into an integer!
			s = v[i_t] if len(str(v[i_s])) == 0 else f'{v[i_s]}{delimiter}{v[i_t]}'
			l.append(s)
		return '\n'.join(l)
	def _injure_decode(self, s):
		l = s.split('\n')
		handlers = list(self._tree.get_children())
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
		self._tree.delete(*self._tree.get_children())

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
			self._tree.insert('', 'end', iid = handler, values = [speaker, color, sentence], tags = (f'"{speaker}"', ))
		self._reorder_line_number()
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
		#self._tree.selection_remove(*self._tree.selection())
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