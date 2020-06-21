import sys
import tkinter as tk
from functools import partial
from pathlib import Path
from tkinter import ttk, font, messagebox, filedialog
#from tkfontchooser import askfont

from . import Scenario

from .character_editor import CharacterEditor
from .dialogue_editor import DialogueEditor
from .info_editor import InfoEditor
from .file import FileState, FileManager
from .extract import Extractor
from .restore import RestoreManager

#TODO: <del>messagebox and filedialog do not block</del>
#use <del>grab_set and wait_window</del> parent

class ScenarioEditorView(tk.Toplevel):
	def __init__(self, master, *args, load_path: Path = None, **kwargs):
		super().__init__(master, *args, **kwargs, class_ = 'ScenarioEditor')

		self._font = font.Font(family = "微軟正黑體", size = 12) #DEFAULT
		self.option_add("*ScenarioEditor*font", self._font)

		ttk.Style().configure("DialogueEditor.Treeview", font = self._font)
		ttk.Style().configure("DialogueEditor.Treeview.Heading", font = self._font)
		ttk.Style().configure("ImageProcessFrame.Treeview", font = self._font)
		ttk.Style().configure("ImageProcessFrame.Treeview.Heading", font = self._font)
		ttk.Style().configure("ScenarioEditor.TNotebook.Tab", font = self._font)
		self._style_font()

		self._menu()

		self.notebook = ttk.Notebook(self, style = 'ScenarioEditor.TNotebook')
		self.notebook.pack(expand = True, fill = tk.BOTH)
	def onclose_register(self, check, f):
		def g():
			a = check() #filemanager check
			if a is not None: #None means "cancel"
				f()
		self.protocol("WM_DELETE_WINDOW", g)
	def set_font_command(self, _ = None):
		#f = askfont()
		#if f:
		#	self.set_font(font.Font(*f))
		#Python tkinter has not had fontchooser
		#So use the tk.call to access the Tk level
		func = self.register(lambda f_s: self.set_font(font.Font(self, f_s)))
		t = self.nametowidget('.')
		t.call('tk', 'fontchooser', 'configure', '-command', func)
		t.call('tk', 'fontchooser', 'configure', '-font', self._font)
		t.call('tk', 'fontchooser', 'show')
	def set_font(self, f):
		conf = f.configure()
		self._font.configure(**conf)
		self._style_font()
	def _style_font(self):
		ttk.Style().configure("DialogueEditor.Treeview", rowheight = self._font.metrics('linespace') + 2)
		ttk.Style().configure("ImageProcessFrame.Treeview", rowheight = self._font.metrics('linespace') + 2)
	def _menu(self):
		self.option_add("*ScenarioEditor*tearOff", False)
		menubar = tk.Menu(self)
		self['menu'] = menubar #meaningful in Tk. self['menu'] returns a plain string in python, though
		self._menubar = menubar #stored in python object

		menu_file = tk.Menu(menubar)
		self._menu_file = menu_file

		menubar.add_cascade(menu = menu_file, label = '檔案')
	@property
	def menubar(self):
		return self._menubar
	@property
	def menu_file(self):
		return self._menu_file
	def add_font_menu(self):
		menubar = self._menubar

		font_menu = tk.Menu(menubar)
		font_menu.add_command(label = '字型設定', command = self.set_font_command)

		menubar.add_cascade(menu = font_menu, label = '字型')

class ScenarioEditor:
	def __init__(self, master, *args, load_path: Path = None, **kwargs):
		fm = FileManager()
		ex = Extractor()
		rm = RestoreManager()
		view = ScenarioEditorView(master, *args, **kwargs)

		fm.set_state_switch_callback(self.filestate_switch_callback)
		rm.set_push_callback(self.rm_push_callback)
		rm.set_restore_callback(self.rm_restore_callback)

		view.bind('<Control-z>', self.restore)

		self.fm = fm
		self.ex = ex
		self.rm = rm
		self.view = view

		view.onclose_register(self._filemanager_check, master.destroy)

		self.build_fm_menu()
		self.build_ex_menu()
		self.build_notebook()

		view.add_font_menu()

		if not load_path:
			self.new_file()
		else:
			self.load_file(load_path)
			if not fm.scenario: #load fail
				self.new_file()
	def filestate_switch_callback(self, state):
		self.view.title(f'{self.fm.filename}{" *" if state is not FileState.Saved else ""}')
	def rm_push_callback(self, m):
		#self._record.append(e)
		fm = self.fm
		if fm.filestate is FileState.Saved:
			fm.filestate = FileState.UnSaved
		elif fm.filestate is FileState.NewUnFiled:
			fm.filestate = FileState.UnFiled
	def restore(self, _):
		success = self.rm.restore_pop()
		if not success:
			messagebox.showwarning("警告", "無法還原至上一步！", parent = self.view)
	def rm_restore_callback(self, m):
		fm = self.fm
		if fm.filestate is FileState.Saved:
			fm.filestate = FileState.UnSaved
	def build_fm_menu(self):
		fm = self.fm
		view = self.view

		for t in fm.provided_command:
			command = getattr(self, f'ask_{t[1]}')
			view.menu_file.add_command(
				label = t[0],
				command = command,
				accelerator = t[2]
			)
			if len(t) >= 4:
				view.bind(t[3], command)
	def build_ex_menu(self):
		fm = self.fm
		ex = self.ex
		view = self.view

		extract_menu = tk.Menu(view.menu_file)
		for i, tname in enumerate(ex.templates, 1):
			partial_command = partial(self.extract_file, tname = tname)
			extract_menu.add_command(
				label = tname,
				command = lambda: partial_command(scenario = fm.scenario, filename = fm.filename),
				accelerator = ('' if i >= 10 else f'Ctrl+{i}')
			)
			if i < 10:
				view.bind(f'<Control-{i}>', lambda _: partial_command(scenario = fm.scenario, filename = fm.filename))
		view.menu_file.add_cascade(menu = extract_menu, label = '匯出')
	def build_notebook(self):
		view = self.view
		rm = self.rm

		self._c_editor = CharacterEditor(view)
		self._d_editor = DialogueEditor(view)
		self._i_editor = InfoEditor(view)
		view.notebook.add(self._c_editor, text = '角色編輯')
		view.notebook.add(self._d_editor, text = '台詞編輯')
		view.notebook.add(self._i_editor, text = '台本資訊編輯')

		self._c_editor.set_caretaker(rm)
		self._d_editor.set_caretaker(rm)
		self._i_editor.set_caretaker(rm)

		self._selected_tab = 0
		view.notebook.bind('<<NotebookTabChanged>>', self._ontabswitch)
	def _ontabswitch(self, _):
		view = self.view

		new_tab = view.notebook.index('current')
		if self._selected_tab == 0 and new_tab != 0:
			self._c_editor.upload_to_scenario()
			if new_tab == 1:
				#self._d_editor.fetch_character_info(self._record) #How to use record?
				self._d_editor.fetch_character_info([])
		if self._selected_tab != 2 and new_tab == 2:
			self._i_editor.fetch_info()
		self._selected_tab = new_tab
	def _filemanager_check(self):
		fm = self.fm

		if fm.filestate is not FileState.Saved and fm.filestate is not FileState.NewUnFiled:
			a = messagebox.askyesnocancel('注意', '是否要儲存變更？', parent = self.view)
			if not a:
				return a #None or False
			if fm.filestate is FileState.UnFiled:
				if not self.ask_save():
					return None
			else:
				self.save_file()
		return True
	def _editor_load_scenario(self, new = False):
		self._c_editor.load_scenario(self.fm.scenario)
		self._d_editor.load_scenario(self.fm.scenario)
		self._i_editor.load_scenario(self.fm.scenario)
		self._d_editor.fetch_character_info([])
		if new:
			self.fm.filestate = FileState.NewUnFiled #prevent new loading memento writing to UnFiled
	def ask_new(self, *args, **kwargs):
		a = self._filemanager_check()
		if a is None:
			return
		self.new_file()
	def new_file(self):
		self.fm.new()
		self._editor_load_scenario(new = True)
	def ask_load(self, *args, **kwargs):
		a = self._filemanager_check()
		if a is None:
			return
		path = filedialog.askopenfile(parent = self.view, filetypes = [('腳本儲存格式 (.json)', '.json')])
		if path is None:
			return
		self.load_file(Path(path.name)) #this 'path.name' is the path in string type
	def load_file(self, path):
		fm = self.fm
		try:
			fm.load(path)
		except Exception as e:
			messagebox.showerror("錯誤", "讀取檔案時發生了錯誤！", parent = self.view)
			return
		self._editor_load_scenario()
	def ask_save(self, *args, **kwargs) -> bool:
		fm = self.fm
		if fm.filestate is FileState.UnFiled or fm.filestate is FileState.NewUnFiled:
			path = filedialog.asksaveasfilename(parent = self.view, filetypes = [('腳本儲存格式 (.json)', '.json')])
			if not path:
				return False
			if not self.make_file(Path(path)):
				return False
		self.save_file()
		return True
	def save_file(self):
		self.upload_scenario()
		self.fm.save()
	def make_file(self, path) -> bool:
		try:
			self.fm.make(path)
		except Exception as e:
			messagebox.showerror("錯誤", "儲存檔案時發生了錯誤！", parent = self.view)
			return False
		return True
	def extract_file(self, tname, scenario, filename):
		ex = self.ex

		self.upload_scenario()
		ex.extract(tname, scenario, filename)
	def upload_scenario(self):
		self._c_editor.upload_to_scenario()
		self._d_editor.upload_to_scenario()
		self._i_editor.upload_to_scenario()

if __name__ == '__main__':
	t = tk.Tk()
	e = ScenarioEditor(t)
	#e.pack()
	t.withdraw()
	#e.set_font(font.nametofont('TkDefaultFont'))
	t.mainloop()