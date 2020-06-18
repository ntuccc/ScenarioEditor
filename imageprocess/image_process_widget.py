import tkinter as tk
from os import getcwd
from pathlib import Path
from tkinter import ttk, simpledialog, filedialog, messagebox, scrolledtext

from .fast_shot import FastShot
from .image_process import ImageProcess

from ..utils import toolbox

class ImageProcessFrame(tk.Frame):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs, class_ = 'ImageProcessFrame')

		self._tree = ttk.Treeview(self, style = 'ImageProcessFrame.Treeview')
		self._tree.pack(expand = True, fill = tk.BOTH)

		self._tree.column('#0', width = 500)

		path_frame = tk.Frame(self)
		path_frame.pack(expand = True)

		self._path_var = tk.StringVar(path_frame)
		self._path_var.set(getcwd().replace('\\', '/'))
		path_label = tk.Label(path_frame, textvariable = self._path_var)
		path_button = tk.Button(path_frame, text = '選取合成路徑', command = self._setpath)

		path_label.grid(row = 0, column = 0)
		path_button.grid(row = 0, column = 1)

		button_frame = tk.Frame(self)
		button_frame.pack()

		self._up_button = tk.Button(button_frame, text = '上移', command = lambda: self._move(up = True))
		self._down_button = tk.Button(button_frame, text = '下移', command = lambda: self._move(up = False))
		self._del_button = tk.Button(button_frame, text = '刪除', fg = 'red', command = lambda: self._tree.delete(*self._tree.selection()))

		shot_button = tk.Button(button_frame, text = '截圖', command = lambda: FastShotDialog(self, title = '截圖'))
		import_button = tk.Button(button_frame, text = '匯入', command = self._import)
		annex_button = tk.Button(button_frame, text = '開始合成', fg = 'red', command = self._annex)

		self._up_button.grid(row = 0, column = 0, padx = 10)
		self._down_button.grid(row = 0, column = 1, padx = 10)
		self._del_button.grid(row = 0, column = 2, padx = 10)
		import_button.grid(row = 1, column = 0, pady = 10)
		shot_button.grid(row = 1, column = 1, pady = 10)
		annex_button.grid(row = 1, column = 2, pady = 10)

		self._tree.bind('<<TreeviewSelect>>', self._onselect)
		self._onselect()

		self._bar = ttk.Progressbar(self, orient = 'horizontal', length = 300, mode = 'determinate')
		self._bar.pack(expand = True, fill = tk.X)
	def _onselect(self, *_):
		selection = self._tree.selection()
		if len(selection) == 0:
			self._up_button['state'] = tk.DISABLED
			self._down_button['state'] = tk.DISABLED
			self._del_button['state'] = tk.DISABLED
		else:
			self._up_button['state'] = tk.NORMAL
			self._down_button['state'] = tk.NORMAL
			self._del_button['state'] = tk.NORMAL
	def _setpath(self):
		path = filedialog.askdirectory(parent = self)
		if path:
			self._path_var.set(path)
	def _move(self, up):
		selection = self._tree.selection()
		index = [self._tree.index(i) for i in selection]
		mapped = toolbox.shift(index, len(self._tree.get_children()), up)
		for s, i in zip((selection if up else reversed(selection)), (index if up else reversed(index))):
			target = mapped[i]
			if target == i:
				continue
			self._tree.move(s, '', target)
	def _import(self):
		l = filedialog.askopenfilenames(parent = self)
		#print(l)
		for n in l:
			self._tree.insert('', 'end', text = n)
	def _annex(self):
		if len(self._tree.get_children()) == 0:
			return
		if not messagebox.askyesno(title = '確認', message = '是否要開始合成？\n合成後會立刻進行文字辨識，請注意google API使用額度限制！'):
			return
		#AnnexShotDialog(self, [self._tree.item(i, 'text') for i in self._tree.get_children()], self._path_var.get())
		filenames = [self._tree.item(i, 'text') for i in self._tree.get_children()]
		path = self._path_var.get()
		self._bar['maximum'] = len(filenames)
		self._bar['value'] = 0
		i = ImageProcess()
		for f in filenames:
			i.add_file(f)
		savename_template, work_code, ite = i.annex_start(save_dir = path)
		img_n = 0
		try:
			while True:
				next(ite)
				self._bar.step(1)
				self._bar.update_idletasks()
		except StopIteration as e:
			img_n = e.value

		text = self._get_text(path, savename_template, work_code, img_n)
		#text = '123\n456'
		TextDialog(self, text)
	@staticmethod
	def _get_text(path, savename_template, work_code, img_n):
		from google.cloud import vision_v1 as vis
		from google.cloud.vision_v1.types import AnnotateImageRequest, Image, Feature
		from google.cloud.vision_v1 import enums
		
		client = vis.ImageAnnotatorClient()
		feature = Feature(type = enums.Feature.Type.TEXT_DETECTION)
		path = Path(path)
		l = []
		for i in range(img_n):
			fullname = path / savename_template.format(work_code = work_code, now_count = i)
			with open(fullname, 'rb') as im:
				image = Image(content = im.read())
			request = AnnotateImageRequest(image = image, features = [feature])
			sol = client.annotate_image(request)
			text = sol.text_annotations[0].description
			l.append(text)
		return '\n'.join(l)

class FastShotDialog(simpledialog.Dialog):
	def body(self, master):
		FastShot(self, path = getcwd().replace('\\', '/')).pack()
	def buttonbox(self):
		tk.Button(self, text = '結束', command = self.cancel).pack()

class AnnexShotDialog(simpledialog.Dialog):
	def __init__(self, master, filenames, save_dir, *args, **kwargs):
		self._filenames = filenames
		self._save_dir = save_dir
		super().__init__(master, *args, **kwargs)
	def process(self):
		i = ImageProcess()
		for f in self._filenames:
			i.add_file(f)
		savename_template, work_code, ite = i.annex_start(save_dir = self._save_dir)
		try:
			while True:
				next(ite)
				self._bar.step(1)
		except StopIteration as e:
			self._result = (savename_template, work_code, e.value)
	def body(self, master):
		self._bar = ttk.Progressbar(self, orient = 'horizontal', length = 300, mode = 'determinate', maximum = len(self._filenames))
		self._bar.pack()
		self.process()
	def buttonbox(self):
		self.b = tk.Button(self, text = '完成', command = self.ok)
		self.b.pack()
	def apply(self):
		self.result = self._result

class TextDialog(simpledialog.Dialog):
	def __init__(self, master, text, *args, **kwargs):
		self._text = text
		super().__init__(master, *args, **kwargs)
	def body(self, master):
		text_frame = scrolledtext.ScrolledText(self)
		text_frame.insert('end', self._text)
		text_frame.pack()
	def buttonbox(self):
		self.b = tk.Button(self, text = '關閉', command = self.cancel)
		self.b.pack()

if __name__ == '__main__':
	t = tk.Tk()
	i = ImageProcessFrame(t)
	i.pack(expand = True, fill = tk.BOTH)
	t.mainloop()