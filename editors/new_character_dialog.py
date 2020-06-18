from tkinter.simpledialog import Dialog
from tkinter import colorchooser, messagebox
import tkinter as tk

class NewCharacterFrame(tk.Frame):
	def __init__(self, parent, defaultcolor = '#ff0000', **kwargs):
		self._defaultcolor = defaultcolor
		#self._chosencolor = self._defaultcolor
		tk.Frame.__init__(self, parent, **kwargs, class_ = 'NewCharacterFrame')

		self.name_var = tk.StringVar(self)
		name_entry_frame = tk.Frame(self)
		name_entry_label = tk.Label(name_entry_frame, text = '名字')
		self.name_entry = tk.Entry(name_entry_frame, width = 15, textvariable = self.name_var)

		name_entry_label.grid(row = 0, column = 0, padx = 1)
		self.name_entry.grid(row = 0, column = 1, padx = 1)

		name_entry_frame.grid(row = 0, column = 0)

		self.color_var = tk.StringVar(self)
		self.color_var.set(self._defaultcolor)
		color_entry_frame = tk.Frame(self)
		color_entry_label = tk.Label(color_entry_frame, text = '顏色')
		self._color_show = tk.Label(color_entry_frame, width = 2, bg = self._defaultcolor)

		def command():
			_, hx = colorchooser.askcolor()
			if hx is not None:
				self.color_var.set(hx)
				self._color_show['bg'] = hx

		color_entry = tk.Button(color_entry_frame, text = '選擇', command = command)

		color_entry_label.grid(row = 0, column = 0, padx = 1)
		self._color_show.grid(row = 0, column = 1, padx = 1)
		color_entry.grid(row = 0, column = 2, padx = 1)

		color_entry_frame.grid(row = 0, column = 1)
	def destroy(self):
		del self.name_var
		del self.color_var
		del self.name_entry
		del self._color_show
		tk.Frame.destroy(self)
	@property
	def name(self):
		return self.name_var.get()
	@name.setter
	def name(self, n):
		self.name_var.set(n)
	@property
	def color(self):
		return self.color_var.get()
	@color.setter
	def color(self, c):
		self.color_var.set(c)
		self._color_show['bg'] = c
	

#https://github.com/python/cpython/blob/master/Lib/tkinter/simpledialog.py
class NewCharacterDialog(Dialog):
	def __init__(self, parent = None, title = None, defaultcolor = '#ff0000'):
		if not parent:
			parent = tk._default_root
		self._defaultcolor = defaultcolor
		Dialog.__init__(self, parent, title)
	def body(self, master):
		self.frame = NewCharacterFrame(self, self._defaultcolor)
		self.frame.pack()
		self.frame.name = '123'
	def destroy(self):
		if self.result is None:
			self.result = (None, None)
		del self.frame
		Dialog.destroy(self)
	def validate(self):
		if self.frame.name == '':
			messagebox.showwarning('提醒', '名字不得為空！', parent = self)
			return False
		self.result = (self.frame.name, self.frame.color)
		return True

def askcharacter(**kwargs):
	d = NewCharacterDialog(**kwargs)
	return d.result

if __name__ == '__main__':
	t = tk.Tk()
	a = askcharacter()
	print(a)