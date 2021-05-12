from enum import Enum, auto

from . import Scenario
from ..utils.decorators import callbackmethod

class FileState(Enum):
	NewUnFiled = auto()
	UnSaved = auto()
	UnFiled = auto()
	Saved = auto()

class FileManager:
	provided_command = [
		('新增檔案', 'new', 'Ctrl+N', '<Control-n>'),
		('開啟檔案', 'load', 'Ctrl+O', '<Control-o>'),
		('儲存檔案', 'save', 'Ctrl+S', '<Control-s>'),
	]
	def __init__(self):
		self.scenario = None
		self.file = None
		self.filename = 'untitled'
		self.filepath = None
		#self._record: list = []
		self._filestate: FileState = FileState.Saved #initial _filestate
	def new(self):
		self.close()
		self.scenario = Scenario()
		self.file = None
		self.filename = 'untitled'
		self.filepath = None
		#self._record = []
		self.set_filestate(FileState.NewUnFiled) #override any change from editors
	def load(self, path):
		try:
			new_f = open(path, 'r+', encoding = 'utf-8')
			new_s = Scenario.load(new_f)
		except Exception as e:
			if not isinstance(e, FileNotFoundError):
				new_f.close()
			raise e
		self.close()
		self.scenario = new_s
		self.file = new_f
		self.filename = path.name
		self.filepath = path
		#self._record = []
		self.set_filestate(FileState.Saved)
	def save(self):
		self.file.seek(0)
		self.scenario.save(self.file, indent = '\t', ensure_ascii = False)
		self.file.truncate()
		self.set_filestate(FileState.Saved)
	def make(self, path):
		if path.suffix == '':
			path = path.with_suffix('.json')
		try:
			new_f = open(path, 'w+', encoding = 'utf-8')
			new_f.close()
			new_f = open(path, 'r+', encoding = 'utf-8')
		except Exception as e:
			#new_f.close()
			raise e
		self.file = new_f
		self.filename = path.name #this 'path.name' is the file name without parent
		self.filepath = path
		self.set_filestate(FileState.UnSaved)
	def close(self):
		try:
			self.file.close()
		except:
			pass
	@property
	def filestate(self):
		return self._filestate
	@callbackmethod
	def set_filestate(self, state):
		self._filestate = state
		return state