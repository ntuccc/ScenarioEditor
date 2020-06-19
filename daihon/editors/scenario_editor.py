import json
import sys
import tkinter as tk
from enum import Enum, auto
from pathlib import Path
from tkinter import ttk, font, messagebox, filedialog
from importlib.resources import open_text, path as resource_path
#from tkfontchooser import askfont

from .character_editor import CharacterEditor
from .dialogue_editor import DialogueEditor
from .info_editor import InfoEditor

from .. import templates
from ..scenario.scenario import Scenario

#TODO: <del>messagebox and filedialog do not block</del>
#use <del>grab_set and wait_window</del> parent

class FileState(Enum):
	NewUnFiled = auto()
	UnSaved = auto()
	UnFiled = auto()
	Saved = auto()

class ScenarioEditorView(tk.Toplevel):
	def __init__(self, master, *args, load_path: Path = None, **kwargs):
		super().__init__(master, *args, **kwargs, class_ = 'ScenarioEditor')

		self._menu()

		self._font = font.Font(family = "微軟正黑體", size = 12) #DEFAULT
		self.option_add("*ScenarioEditor*font", self._font)

		ttk.Style().configure("DialogueEditor.Treeview", font = self._font)
		ttk.Style().configure("DialogueEditor.Treeview.Heading", font = self._font)
		ttk.Style().configure("ImageProcessFrame.Treeview", font = self._font)
		ttk.Style().configure("ImageProcessFrame.Treeview.Heading", font = self._font)
		ttk.Style().configure("ScenarioEditor.TNotebook.Tab", font = self._font)
		self._style_font()

		self._notebook = ttk.Notebook(self, style = 'ScenarioEditor.TNotebook')
		self._notebook.pack(expand = True, fill = tk.BOTH)

		self._c_editor = CharacterEditor(self)
		self._d_editor = DialogueEditor(self)
		self._i_editor = InfoEditor(self)

		self._notebook.add(self._c_editor, text = '角色編輯')
		self._notebook.add(self._d_editor, text = '台詞編輯')
		self._notebook.add(self._i_editor, text = '台本資訊編輯')

		self._filemanager_init()

		if not load_path:
			self._new_scenario()
		else:
			self._load_scenario(load_path)
			if not self._scenario: #load fail
				self._new_scenario()

		self._selected_tab = 0
		self._notebook.bind('<<NotebookTabChanged>>', self._ontabswitch)
	def _ontabswitch(self, _):
		new_tab = self._notebook.index('current')
		if self._selected_tab == 0 and new_tab != 0:
			self._c_editor.upload_to_scenario()
			if new_tab == 1:
				self._d_editor.fetch_character_info(self._record)
		if self._selected_tab != 2 and new_tab == 2:
			self._i_editor.fetch_info()
		self._selected_tab = new_tab
	def _filemanager_init(self):
		self._scenario = None
		self._file = None
		self._filename = 'untitled'
		self._record: list = []
		self._filestate: FileState = FileState.Saved

		self._c_editor.callback = self._action_callback
		self._d_editor.callback = self._action_callback
		self._i_editor.callback = self._action_callback
	def _action_callback(self, e):
		self._record.append(e)
		if self._filestate is FileState.Saved:
			self._switch_state(FileState.UnSaved)
		elif self._filestate is FileState.NewUnFiled:
			self._switch_state(FileState.UnFiled)
	def _filemanager_check(self):
		if self._filestate is not FileState.Saved and self._filestate is not FileState.NewUnFiled:
			a = messagebox.askyesnocancel('注意', '是否要儲存變更？', parent = self)
			if not a:
				return a #None or False
			if self._filestate is FileState.UnFiled:
				if not self.ask_save():
					return None
			else:
				self._save_scenario()
		return True
	def onclose_register(self, f):
		def g():
			a = self._filemanager_check()
			if a is not None: #None means "cancel"
				f()
		self.protocol("WM_DELETE_WINDOW", g)
	def ask_load(self, _ = None):
		a = self._filemanager_check()
		if a is None:
			return
		path = filedialog.askopenfile(parent = self, filetypes = [('腳本儲存格式 (.json)', '.json')])
		if path is None:
			return
		self._load_scenario(Path(path.name)) #this 'path.name' is the path in string type
	def ask_new(self, _ = None):
		a = self._filemanager_check()
		if a is None:
			return
		self._new_scenario()
	def ask_save(self, _ = None):
		if self._filestate is FileState.UnFiled or self._filestate is FileState.NewUnFiled:
			path = filedialog.asksaveasfilename(parent = self, filetypes = [('腳本儲存格式 (.json)', '.json')])
			if not path:
				return False
			if not self._makefile(Path(path)):
				return False
		self._save_scenario()
		return True
	def _makefile(self, path):
		if path.suffix == '':
			path = path.with_suffix('.json')
		try:
			new_f = open(path, 'w+', encoding = 'utf-8')
			new_f.close()
			new_f = open(path, 'r+', encoding = 'utf-8')
		except Exception as e:
			messagebox.showerror("錯誤", "儲存檔案時發生了錯誤！", parent = self)
			print(e)
			#new_f.close()
			return False
		self._file = new_f
		self._filename = path.name #this 'path.name' is the file name without parent
		self._switch_state(FileState.UnSaved)
		return True
	def _load_scenario(self, path):
		try:
			new_f = open(path, 'r+', encoding = 'utf-8')
			new_s = Scenario.load(new_f)
		except Exception as e:
			messagebox.showerror("錯誤", "讀取檔案時發生了錯誤！", parent = self)
			if not isinstance(e, FileNotFoundError):
				new_f.close()
			return
		self._close_file()
		self._scenario = new_s
		self._file = new_f
		self._filename = path.name
		self._record = []
		self._switch_state(FileState.Saved)
		self._editor_load_scenario()
	def _new_scenario(self): #noexcept
		self._close_file()
		self._scenario = Scenario()
		self._file = None
		self._filename = 'untitled'
		self._record = []
		self._editor_load_scenario()
		self._switch_state(FileState.NewUnFiled) #override any change from editors
	def _save_scenario(self):
		self._c_editor.upload_to_scenario()
		self._d_editor.upload_to_scenario()
		self._i_editor.upload_to_scenario()
		self._file.seek(0)
		self._scenario.save(self._file, indent = '\t', ensure_ascii = False)
		self._file.truncate()
		self._switch_state(FileState.Saved)
	def _switch_state(self, s):
		self._filestate = s
		self.title(f'{self._filename}{" *" if s is not FileState.Saved else ""}')
	def _close_file(self):
		try:
			self._file.close()
		except:
			pass
	def _editor_load_scenario(self):
		self._c_editor.load_scenario(self._scenario)
		self._d_editor.load_scenario(self._scenario)
		self._i_editor.load_scenario(self._scenario)
		self._d_editor.fetch_character_info([])
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
		#menu_file.add_command(label = '匯出', command = self.extract, accelerator = 'Ctrl+E')

		#self.bind('<Control-e>', self.extract)

		menu_file.add_cascade(menu = self._extract_menu(menu_file), label = '匯出')

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
	def _extract_menu(self, menu_file):
		extract_file = tk.Menu(menu_file)
		with open_text(templates, 'templates.json') as file:
			#After Py 3.7 dict preserves the order
			self._templates = json.load(file)
		for i, tname in enumerate(self._templates, 1):
			extract_file.add_command(label = tname, command = lambda n = tname: self.extract(n), accelerator = ('' if i >= 10 else f'Ctrl+{i}'))
			if i < 10:
				self.bind(f'<Control-{i}>', lambda _, n = tname: self.extract(n))
		return extract_file
	def extract(self, tname):
		if tname not in self._templates:
			return
		self._c_editor.upload_to_scenario()
		self._d_editor.upload_to_scenario()
		self._i_editor.upload_to_scenario()
		print(tname)
		getattr(self, f'_extract_with_{self._templates[tname]["renderer"]}')(tname)
	def _extract_with_jinja2(self, tname):
		from jinja2 import Environment, FileSystemLoader
		from jinja2.ext import i18n, do, loopcontrols, with_
		info = self._templates[tname]
		print(info)
		if not hasattr(self, f'_extract_env_{tname}'):
			with resource_path(templates, '.') as path:
				setattr(self, f'_extract_env_{tname}', Environment(loader = FileSystemLoader(str(path)), extensions = [i18n, do, loopcontrols, with_], **info['env_param']))
		template = getattr(self, f'_extract_env_{tname}').get_template(info['filename'])
		with open(f'{Path(self._filename).stem}.{info["suffix"]}', 'w', encoding = 'utf-8') as file:
			file.write(template.render({'scenario': self._scenario}))
	def _extract_with_docxtpl(self, tname):
		from jinja2 import Environment
		from jinja2.ext import i18n, do, loopcontrols, with_
		from docxtpl import DocxTemplate
		info = self._templates[tname]
		if not hasattr(self, f'_extract_env_{tname}'):
			setattr(self, f'_extract_env_{tname}', Environment(extensions = [i18n, do, loopcontrols, with_], **info['env_param']))
		with resource_path(templates, info['filename']) as template_path:
			doctemplate = DocxTemplate(str(template_path))
		doctemplate.render({'scenario': self._scenario}, getattr(self, f'_extract_env_{tname}'))
		doctemplate.save(f'{Path(self._filename).stem}.{info["suffix"]}')

class FileManager:
	provided_command = [
		('新增檔案', 'new', 'Ctrl+N', '<Control-n>'),
		('開啟檔案', 'load', 'Ctrl+O', '<Control-o>'),
		('儲存檔案', 'save', 'Ctrl+S', '<Control-s>'),
	]
	def new(self):
		pass
	def load(self):
		pass
	def save(self):
		pass

class Extractor:
	pass

class ScenarioEditor:
	def __init__(self, master, *args, **kwargs):
		fm = FileManager()
		ex = Extractor()
		view = ScenarioEditorView(master, *args, **kwargs)

		self.fm = fm
		self.ex = ex
		self.view = view

		view.onclose_register(master.destroy)

		self.build_fm_menu()

		view.add_font_menu()
	def build_fm_menu(self):
		fm = self.fm
		view = self.view

		for t in fm.provided_command:
			command = getattr(self, f'ask_{t[1]}')
			view.menu_file.add_command(label = t[0], command = command, accelerator = t[2])
			if len(t) >= 4:
				view.bind(t[3], command)
	def ask_new(self, *args, **kwargs):
		pass
	def ask_load(self, *args, **kwargs):
		pass
	def ask_save(self, *args, **kwargs):
		pass

if __name__ == '__main__':
	t = tk.Tk()
	e = ScenarioEditor(t)
	#e.pack()
	t.withdraw()
	#e.set_font(font.nametofont('TkDefaultFont'))
	t.mainloop()