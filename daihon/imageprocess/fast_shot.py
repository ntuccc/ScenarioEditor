import keyboard
import pyscreenshot as ImageGrab
import tkinter as tk
from itertools import count
from pathlib import Path
from PIL import Image, ImageTk
from time import sleep
from tkinter import filedialog, messagebox
from typing import Tuple

from .tkapp import AppBase

class FastShot(tk.Frame):
	_counter = None
	_img_window: tk.Toplevel = None
	def __init__(self, master = None, *args, path = '', **kwargs):
		super().__init__(master, *args, **kwargs)

		self._counter = count()
		self._img_window = None

		open_dir = tk.Frame(self)
		open_dir_text = tk.Label(open_dir, text = '選取路徑')
		open_dir_dirname_var = tk.StringVar(open_dir)
		open_dir_dirname_var.set(path)
		open_dir_dirname = tk.Label(open_dir, textvariable = open_dir_dirname_var, wraplength = 200)
		open_dir_button = tk.Button(open_dir, text = '瀏覽', command = (lambda: self.ask_dir(open_dir_dirname_var)))
		#open_dir_button = tk.Button(open_dir, text = '瀏覽', command = (lambda: (open_dir_dirname_var.set(path := filedialog.askdirectory())) if path != '' else None))
		###
		open_dir_text.grid(row = 0, column = 0)
		open_dir_dirname.grid(row = 0, column = 1)
		open_dir_button.grid(row = 0, column = 2)

		choose_key = tk.Frame(self)
		choose_key_text = tk.Label(choose_key, text = '按下選擇並敲下鍵盤以更改熱鍵')
		choose_key_keyname_var = tk.StringVar(choose_key)
		choose_key_keyname_var.set('space')
		choose_key_keyname = tk.Label(choose_key, textvariable = choose_key_keyname_var)
		choose_key_button = tk.Button(choose_key, text = '選擇', command = (lambda: choose_key_keyname_var.set(read_hotkey())))
		###
		choose_key_text.grid(row = 0, column = 0)
		choose_key_keyname.grid(row = 0, column = 1)
		choose_key_button.grid(row = 0, column = 2)

		hotkey_everytime = tk.Frame(self)
		hotkey_everytime_text1 = tk.Label(hotkey_everytime, text = '每按')
		hotkey_everytime_time_var = tk.IntVar(hotkey_everytime)
		hotkey_everytime_time_var.set(1)
		hotkey_everytime_time = tk.Entry(hotkey_everytime, width = 4, textvariable = hotkey_everytime_time_var)
		hotkey_everytime_text2 = tk.Label(hotkey_everytime, text = '次熱鍵才觸發')
		###
		hotkey_everytime_text1.grid(row = 0, column = 0)
		hotkey_everytime_time.grid(row = 0, column = 1)
		hotkey_everytime_text2.grid(row = 0, column = 2)

		naming = tk.Frame(self)
		naming_text = tk.Label(naming, text = '檔名格式')
		naming_format_var = tk.StringVar(naming)
		naming_format_var.set('{:04d}.png')
		naming_format = tk.Entry(naming, textvariable = naming_format_var)
		naming_counter_text = tk.Label(naming, text = '計數器')
		naming_counter_var = tk.StringVar(naming)
		naming_counter_var.set('0')
		naming_counter_vcmd = (naming.register(lambda code, content: int(code) != 1 or content.isdigit()), '%d', '%S')
		naming_counter = tk.Entry(naming, textvariable = naming_counter_var, width = 5, validate = 'key', validatecommand = naming_counter_vcmd)
		###
		naming_text.grid(row = 0, column = 0)
		naming_format.grid(row = 0, column = 1)
		naming_counter_text.grid(row = 0, column = 2)
		naming_counter.grid(row = 0, column = 3)

		force_top = tk.Frame(self)
		force_top_text1 = tk.Label(force_top, text = '截圖後是否強制置頂截圖畫面？', fg = 'red')
		force_top_var = tk.StringVar(force_top)
		force_top_var.set('0')
		force_top_button = tk.Checkbutton(force_top, variable = force_top_var)
		force_top_text2 = tk.Label(force_top, text = '（若遇到視窗跑掉的問題再行勾選）')
		###
		force_top_text1.grid(row = 0, column = 0)
		force_top_button.grid(row = 0, column = 1, rowspan = 2)
		force_top_text2.grid(row = 1, column = 0)

		enable_hotkey_button = tk.Button(self, text = '點擊以啟動熱鍵')
		self._hookHandler = None
		callback_by_hotkey = lambda: self.onShot(
			path = open_dir_dirname_var.get(),
			press_time = (next(self._counter), hotkey_everytime_time_var.get()),
			naming_format = naming_format,
			naming_counter = naming_counter,
			naming_counter_var = naming_counter_var,
			force = force_top_var.get() == '1',
			blend = 1)
		callback_by_button = lambda: self.onShot(
			path = open_dir_dirname_var.get(),
			press_time = (0, 0),
			naming_format = naming_format,
			naming_counter = naming_counter,
			naming_counter_var = naming_counter_var,
			force = force_top_var.get() == '1',
			blend = 1)
		def enable():
			if self._hookHandler is not None:
				choose_key_button['state'] = tk.NORMAL
				hotkey_everytime_time['state'] = tk.NORMAL
				enable_hotkey_button['text'] = '點擊以啟動熱鍵'
				keyboard.remove_hotkey(self._hookHandler)
				self._hookHandler = None
			else:
				self._counter = count()
				choose_key_button['state'] = tk.DISABLED
				hotkey_everytime_time['state'] = tk.DISABLED
				enable_hotkey_button['text'] = '點擊以關閉熱鍵'
				self._hookHandler = keyboard.add_hotkey(choose_key_keyname_var.get().replace(',', 'comma'), callback_by_hotkey)
		enable_hotkey_button['command'] = enable

		shot_button = tk.Button(self, text = '點擊直接截圖', command = callback_by_button)

		open_dir.pack(pady = 3, ipady = 2)
		choose_key.pack(pady = 3)
		hotkey_everytime.pack(pady = 3)
		naming.pack(pady = 3)
		force_top.pack(pady = 3)
		enable_hotkey_button.pack(pady = 3)
		shot_button.pack(pady = 3)
	def destroy(self):
		if self._hookHandler:
			keyboard.remove_hotkey(self._hookHandler)
			self._hookHandler = None
		super().destroy()
	@staticmethod
	def ask_dir(strvar: tk.StringVar):
		s = filedialog.askdirectory()
		if s != '':
			strvar.set(s)
	def onShot(self, path: str, press_time: Tuple[int, int], naming_format: tk.Entry, naming_counter: tk.Entry, naming_counter_var: tk.StringVar, force: bool, blend: int):
		#'blend' is a test feature (2 is in alpha, 1 is in beta)
		#2: white bg when dragging and black choosing rect
		#1: rect with border to indicate the choosing place
		#0: do not blend
		#blend == 2 is very inefficient and lag when choosing a large range
		if path == '':
			return None
		if press_time[1] > 0 and press_time[0] % press_time[1] != 0:
			return None
		if self._img_window is not None:
			return None
		#print(path)
		path = Path(path)
		img = ImageGrab.grab()
		self._img_window = tk.Toplevel(self)
		self._img_window.attributes('-fullscreen', True)
		if force:
			self._img_window.lift()
			self._img_window.attributes('-topmost', True)
		self._img_tk = ImageTk.PhotoImage(img)
		if blend == 2 or blend == 1:
			f = tk.Canvas(self._img_window, width = img.size[0], height = img.size[1])
			f.create_image((0, 0), image = self._img_tk, anchor = tk.NW)
		else:
			f = tk.Label(self._img_window, image = self._img_tk)
			#f.image = self._img_tk #keep reference, or the img won't show out
		f.pack()

		f.update()
		if blend == 2:
			print((f.winfo_width(), f.winfo_height()))
			white_bg = Image.new('RGBA', (f.winfo_width(), f.winfo_height()), 'white')
			white_bg.putalpha(64)
			self._white_bg_img_tk = ImageTk.PhotoImage(white_bg)

		x1, y1, x2, y2 = 0, 0, 0, 0
		funcID = None
		#blend == 2
		blackID = None
		#blend == 1
		mark_rectID = None
		rect_width = 1
		def drawblack(e1, e2):
			nonlocal blackID
			size = (abs(e1.x - e2.x) + 1, abs(e1.y - e2.y) + 1)
			corner = (min(e1.x, e2.x), min(e1.y, e2.y))
			if blend == 2:
				black_bg = Image.new('RGBA', size, 'black')
				black_bg.putalpha(32)
				self._black_bg_img_tk = ImageTk.PhotoImage(black_bg)
				if blackID is not None:
					f.itemconfigure(blackID, image = self._black_bg_img_tk)
					f.coords(blackID, corner)
				blackID = f.create_image(corner, image = self._black_bg_img_tk, anchor = tk.NW)
			elif blend == 1:
				f.coords(mark_rectID, *corner, corner[0] + size[0] - rect_width, corner[1] + size[1] - rect_width)
		def onEsc(*args, **kwargs):
			self._img_window.destroy()
			self._img_window = None
		def onRelease(e):
			nonlocal x2, y2
			x2, y2 = e.x, e.y

			f = naming_format.get()
			now_count_str = naming_counter_var.get()
			now_count = 0 if not now_count_str.isdigit() else int(now_count_str)
			#now_count = 0 if not (now_count_str := naming_counter_var.get()).isdigit() else int(now_count_str)
			naming_counter_var.set(now_count + 1)
			img_new = img.crop((min(x1, x2), min(y1, y2), max(x1, x2) + 1, max(y1, y2) + 1))

			if not path.exists():
				messagebox.showerror('錯誤', '儲存路徑不存在！')
			else:
				try:
					img_new.save(path / f.format(now_count))
				except:
					messagebox.showwarning('警告', '檔案儲存失敗\n請檢查檔名格式是否錯誤\n並確認有無圖片副檔名(.jpg或.png等)')

			naming_format['state'] = tk.NORMAL
			naming_counter['state'] = tk.NORMAL

			onEsc()
		def onPress(e):
			nonlocal x1, y1, mark_rectID
			x1, y1 = e.x, e.y
			self._img_window.unbind(funcID)
			self._img_window.bind('<ButtonRelease-1>', onRelease)

			if blend == 2:
				self._img_window.bind('<Motion>', (lambda event: drawblack(event, e)))
				f.create_image((0, 0), image = self._white_bg_img_tk, anchor = tk.NW)
				drawblack(e, e)
			elif blend == 1:
				self._img_window.bind('<Motion>', (lambda event: drawblack(event, e)))
				mark_rectID = f.create_rectangle(x1, y1, x1 + 1 - rect_width, y1 + 1 - rect_width, outline = 'red')

			naming_format['state'] = tk.DISABLED
			naming_counter['state'] = tk.DISABLED
		funcID = self._img_window.bind('<Button-1>', onPress)
		self._img_window.bind('<Button-3>', onEsc)
		self._img_window.protocol('WM_DELETE_WINDOW', onEsc)

def read_hotkey():
	t = keyboard.stash_state()
	s = keyboard.read_hotkey()
	keyboard.restore_state(t)
	return s

if __name__ == '__main__':
	t = tk.Tk()
	t.title('截圖')
	a = FastShot(t)
	a.pack(expand = True)
	a.mainloop()