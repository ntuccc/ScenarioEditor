import tkinter as tk

class AppBase():
	_close: bool = False
	_master: tk.Misc #tk.Misc is the common base of tk.Tk and tk.Toplevel, and having method winfo_toplevel
	_now_mainloop = None
	def __init__(self, master: tk.Misc = None):
		if master is None:
			master = tk.Tk()
		self._master = master
		self._master.winfo_toplevel().protocol('WM_DELETE_WINDOW', self.onclosing)
		self.main()
	def main(self):
		#to be overriden
		pass
	def mainloop(self, widget):
		self._now_mainloop = widget
		widget.mainloop()
		self._now_mainloop = None
	def onclosing(self):
		self._close = True
		if self._now_mainloop is not None:
			self._now_mainloop.quit()