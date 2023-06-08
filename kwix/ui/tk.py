import tkinter as tk
from tkinter import ttk
from kwix.logic import Logic, Context, Window

import threading
import queue

import kwix.ui.builder
import kwix.ui.builder.tk

from kwix.util import ThreadRouter
import kwix.logic

import pkg_resources
from PIL import Image, ImageTk


def get_logo():
	return Image.open(pkg_resources.resource_filename('kwix', 'logo.jpg'))

def run_periodically(root: tk.Tk, interval_ms: int, action):
	def on_timer():
		root.after(interval_ms, on_timer)
		action()
	on_timer()




class KwixWindow(kwix.logic.Window):
	actions = []

	def __init__(self, logic: Logic):
		self._root = None
		self._logic = logic
		self._action_context = kwix.logic.Context(logic, self)
		self._create_root()

	def _create_root(self):
		self._root = tk.Tk()
		self._root.wm_iconphoto(False, ImageTk.PhotoImage(get_logo()))
		self._forbid_minimize()
		self._root.protocol("WM_DELETE_WINDOW", self.hide)
		self._root.title('Kwix!')
		self._root.geometry('500x200')
		self._root.columnconfigure(0, weight=1)
		self._root.rowconfigure(0, weight=1)
		self._root.bind('<Escape>', self.hide)
		self._root.bind('<Return>', self._on_enter)

		self._mainframe = ttk.Frame(self._root)
		self._mainframe.grid(column=0, row=0, sticky='nsew')
		self._mainframe.rowconfigure(1, weight=1)
		self._mainframe.columnconfigure(0, weight=1)

		self._search_query = tk.StringVar()
		self._search_query.trace_add("write", self._on_query_entry_type)
		self._search_entry = ttk.Entry(self._mainframe, textvariable=self._search_query)
		self._search_entry.grid(column=0, row=0, sticky='ew')
		self._search_entry.bind('<Alt-KeyPress-Return>', lambda *args: self._edit_selected_action())
		for key in ('<Up>', '<Down>'): 
			self._search_entry.bind(key, self._on_search_entry_updown)

		self._result_list = tk.StringVar()
		self._result_listbox = tk.Listbox(
			self._mainframe, listvariable=self._result_list, takefocus=False, selectmode='browse')
		self._result_listbox.grid(column=0, row=1, sticky='nsew')
		self._result_listbox.bind("<Button-1>", self._on_list_left_click)
		self._result_listbox.bind('<Button-3>', self._on_list_right_click)
		self._on_query_entry_type()

		self._root.withdraw()

	def _on_search_entry_updown(self, event):
		sel = newsel = self._result_listbox.curselection()[0]
		if 'Up' == event.keysym:
			if sel > 0:
				newsel = sel - 1
		elif 'Down' == event.keysym:
			if sel + 1 < self._result_listbox.size():
				newsel = sel + 1
		if sel != newsel:
			self._result_listbox.selection_clear(sel)
			self._result_listbox.selection_set(newsel)

	def _on_list_left_click(self, event):
		self._select_item_at_y_pos(event.y)
		self._on_enter()

	def _on_list_right_click(self, event):
		self._select_item_at_y_pos(event.y)
		self._edit_selected_action()

	def _edit_selected_action(self):
		action = self._get_selected_action()
		if not action:
			return
		
		window = tk.Toplevel(self._root)
		window.title(action.title + ': edit')
		window.geometry("500x500")
		window.columnconfigure(0, weight=1)
		window.rowconfigure(1, weight=1)
		window.transient(self._root)

		data = ttk.Frame(window, padding=8)
		data.grid(column=0, row=0, sticky='nsew')

		control = ttk.Frame(window, padding=8)
		control.grid(column=0, row=2, sticky='nsew')
		control.columnconfigure(0, weight=1)

		ok = ttk.Button(control, text="OK")
		ok.grid(column=1, row=0, padx=4)

		cancel = ttk.Button(control, text='Cancel')
		cancel.grid(column=2, row=0, padx=4)


		dialog = kwix.ui.builder.tk.DialogBuilder(data)
		action.action_type.create_editor(dialog)
		dialog.read_value(action)

		window.wait_visibility()
		window.grab_set()
		window.focus_set()
		window.wait_window()
		

	def _get_selected_action(self):
		selection = self._result_listbox.curselection()
		if not selection:
			return None
		try:
			return self._action_list[selection[0]]
		except IndexError:
			return None

	def _select_item_at_y_pos(self, y):
		self._result_listbox.selection_clear(0,tk.END)
		self._result_listbox.selection_set(self._result_listbox.nearest(y))

	def run(self):
		self._thread_router = ThreadRouter()
		run_periodically(self._root, 10, self._thread_router.process)
		self._root.mainloop()

	def _forbid_minimize(self):
		try:
			self._root.attributes("-toolwindow", True)
		except:
			pass
		# self._root.attributes('-type', 'dock')

	def _on_query_entry_type(self, name = None, index = None, mode = None):
		self._action_list = self._logic.action_search(self._search_query.get())
		self._result_list.set([action.title for action in self._action_list])
		if self._action_list:
			self._result_listbox.select_clear(0, tk.END)
			self._result_listbox.selection_set(0)
		self._result_listbox.see(0)

	def is_visible(self):
		return self._root and self._root.winfo_viewable()

	def show(self):
		self._thread_router.exec(self._do_show)

	def _do_show(self):
		self._search_entry.focus_set()
		self._search_entry.select_range(0, 'end')
		self._root.deiconify()
		self._root.attributes('-topmost', True)

	def hide(self, *args):
		self._thread_router.exec(self._root.withdraw)

	def quit(self):
		self._thread_router.exec(self._root.destroy)

	def _on_enter(self, *args):
		action = self._get_selected_action()
		if action:
			action.go(self._action_context)


