import tkinter as tk
from tkinter import ttk

import pkg_resources
from PIL import Image, ImageTk

import kwix
import kwix.ui
import kwix.ui.tk
from kwix.util import ThreadRouter
from kwix import ActionRegistry, Action


def get_logo():
	return Image.open(pkg_resources.resource_filename('kwix', 'logo.jpg'))

def run_periodically(root: tk.Tk, interval_ms: int, action):
	def on_timer():
		root.after(interval_ms, on_timer)
		action()
	on_timer()




class Window(kwix.ui.Window):
	actions = []

	def __init__(self, action_registry: ActionRegistry):
		self._root = None
		self._action_registry: ActionRegistry = action_registry
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

		# scroller = ttk.Frame(window)
		# scroller.grid(column = 0, row = 0)
		# scroller.rowconfigure(0, weight = 1)
		# scroller.columnconfigure(1, weight=1)
		
		#scrollbar = ttk.Scrollbar(scroller, orient = 'vertical')
		#scrollbar.grid(row=0, column=1)


		data = ttk.Frame(window, padding=8)
		data.grid(column=0, row=0, sticky='nsew')
		#data.bind("<Configure>", lambda e: canvas.configure(
        #scrollregion=canvas.bbox("all")
		#data = ttk.Widget(..., yscrollcommand = scrol.set)
		# v.config(command=w.yview)
		# https://ru.stackoverflow.com/questions/1333158/%D0%9A%D0%B0%D0%BA-%D1%80%D0%B5%D0%B0%D0%BB%D0%B8%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D1%8C-scrollbar-%D0%B4%D0%BB%D1%8F-frame


		dialog = kwix.ui.tk.DialogBuilder(data)
		action.action_type.create_editor(dialog)
		dialog.read_value(action)

		control = ttk.Frame(window, padding=8)
		control.grid(column=0, row=2, sticky='nsew')
		control.columnconfigure(0, weight=1)

		def on_ok(*args):
			dialog.update_value(action)
			window.destroy()
			self._on_query_entry_type()
		window.bind('<Return>', on_ok)
		ok = ttk.Button(control, text="OK", command = on_ok)
		ok.grid(column=1, row=0, padx=4)

		def on_cancel(*args):
			window.destroy()
		window.bind('<Escape>', on_cancel)
		cancel = ttk.Button(control, text='Cancel', command = on_cancel)
		cancel.grid(column=2, row=0, padx=4)

		window.wait_visibility()
		window.grab_set()
		window.focus_set()
		window.wait_window()
		

	def _get_selected_action(self) -> Action | None:
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
		self._action_list = self._action_registry.search(self._search_query.get())
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
		self._on_query_entry_type()

	def hide(self, *args):
		self._thread_router.exec(self._root.withdraw)

	def quit(self) -> None:
		self._thread_router.exec(self._root.destroy)

	def _on_enter(self, *args):
		action: Action = self._get_selected_action()
		if action:
			self.hide()
			action.run()








class DialogEntry(kwix.ui.DialogEntry):
	def __init__(self, label: ttk.Label, string_var: tk.StringVar):
		self._label = label
		self._string_var = string_var
	def set_title(self, text: str):
		self._label.config(text = text)
	def get_value(self):
		return self._string_var.get()
	def set_value(self, value):
		self._string_var.set(value)
	def on_change(self, func: callable):
		self._string_var.trace_add("write", lambda *args, **kwargs: func(self._string_var.get()))



class DialogBuilder(kwix.ui.DialogBuilder):
	def __init__(self, root: ttk.Frame):
		super().__init__()
		self._root = root
		self._root.columnconfigure(0, weight=1)
		self._widget_count = 0

	def create_entry(self, title: str, on_change: callable = None) -> DialogEntry:
		label = ttk.Label(self._root, text=title)
		label.grid(column=0, row=self._widget_count, sticky='ew')
		self._widget_count+=1

		string_var = tk.StringVar(self._root)
		entry = ttk.Entry(self._root, textvariable=string_var)
		entry.grid(column=0, row=self._widget_count, sticky='ew')
		self._widget_count += 1
		if self._widget_count == 2:
			entry.focus_set()

		separator = ttk.Label(self._root, text='')
		separator.grid(column=0, row=self._widget_count, sticky='ew')
		self._widget_count+=1

		result = DialogEntry(label, string_var)
		if on_change:
			result.on_change(on_change)
		return result
	
	def create_section(self, title: str, create_dialog: callable):
		row_frame = tk.Frame(self._root)
		row_frame.grid(column = 0, row=self._widget_count)
		self._widget_count+=1

		content_frame = tk.Frame(row_frame)
		content_frame.grid(column=1, row=0)

		dialog_builder = DialogBuilder(content_frame)
		create_dialog(dialog_builder)
		self.on_read_value(dialog_builder.read_value)
		self.on_update_value(dialog_builder.update_value)





