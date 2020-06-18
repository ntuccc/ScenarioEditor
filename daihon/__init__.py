import tkinter as tk
from .editors.scenario_editor import ScenarioEditor

def main():
	t = tk.Tk()
	e = ScenarioEditor(t)
	#e.pack()
	t.withdraw()
	e.onclose_register(t.destroy)
	#e.set_font(font.nametofont('TkDefaultFont'))
	t.mainloop()