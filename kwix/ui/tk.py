import tkinter as tk
from tkinter import ttk
from typing import Callable, Any, cast

import pkg_resources
from PIL import Image, ImageTk

import time
import kwix
import kwix.ui
from kwix import DialogBuilder, Selector, ok_text, cancel_text, DialogWidget
import kwix.ui.tk
from kwix.util import ThreadRouter
from kwix import Item, ItemSource


def get_logo():
	return Image.open(pkg_resources.resource_filename('kwix', 'logo.jpg'))


def run_periodically(root: tk.Tk, interval_ms: int, action):
	def on_timer():
		root.after(interval_ms, on_timer)
		action()
	on_timer()


class Ui(kwix.Ui):
	def __init__(self):
		super().__init__()
		self.root = tk.Tk()
		self.root.wm_iconphoto(False, ImageTk.PhotoImage(get_logo()))
		self.root.title('Kwix!')
		self.root.withdraw()
	def run(self):
		self._thread_router = ThreadRouter()
		run_periodically(self.root, 10, self._thread_router.process)
		self.root.mainloop()
	def selector(self) -> kwix.Selector:
		return Selector(self)
	def dialog(self, create_dialog: Callable[[DialogBuilder], None]) -> None:
		return Dialog(self, create_dialog)
	def stop(self):
		self._thread_router.exec(self.root.destroy)


class ModalWindow:
	def __init__(self, parent: Ui):
		self.parent = parent
		self.title = 'kwix'
		self._create_window()
	def _create_window(self):
		self._window = tk.Toplevel(self.parent.root)
		# self._widow.wm_iconphoto(False, ImageTk.PhotoImage(get_logo()))
		#self._window.transient(self.parent.root)
		self._window.title(self.title)
		self._window.geometry('500x200')
		self._window.columnconfigure(0, weight=1)
		self._window.rowconfigure(0, weight=1)
		self._window.bind('<Escape>', cast(Any, self.hide))
		self._window.withdraw()
	def show(self):
		self.parent._thread_router.exec(self._do_show)
	def _do_show(self):
		self._window.title(self.title)
		self._window.deiconify()
		self._window.focus_set()
	def hide(self, *args):
		self.parent._thread_router.exec(self._window.withdraw)



class Selector(kwix.Selector, ModalWindow):
	actions = []

	def __init__(self, parent: Ui, item_source: ItemSource = ItemSource()):
		ModalWindow.__init__(self, parent)
		kwix.Selector.__init__(self, item_source)
		self.result: Item | None = None
		self._init_window()

	def _init_window(self):
		self._window.bind('<Return>', cast(Any, lambda x: self._on_enter(0)))
		self._window.bind('<Alt-KeyPress-Return>', cast(Any, lambda x: self._on_enter(1)))

		self._mainframe = ttk.Frame(self._window)
		self._mainframe.grid(column=0, row=0, sticky='nsew')
		self._mainframe.rowconfigure(1, weight=1)
		self._mainframe.columnconfigure(0, weight=1)

		self._search_query = tk.StringVar()
		self._search_query.trace_add("write", self._on_query_entry_type)
		self._search_entry = ttk.Entry(
			self._mainframe, textvariable=self._search_query)
		self._search_entry.grid(column=0, row=0, sticky='ew')
		for key in ('<Up>', '<Down>'):
			self._search_entry.bind(key, self._on_search_entry_updown)

		self._result_list = tk.StringVar()
		self._result_listbox = tk.Listbox(
			self._mainframe, listvariable=self._result_list, takefocus=False, selectmode='browse')
		self._result_listbox.grid(column=0, row=1, sticky='nsew')
		self._result_listbox.bind("<Button-1>", self._on_list_left_click)
		self._result_listbox.bind("<Button-3>", self._on_list_right_click)
		self._on_query_entry_type()
		

	def _hide(self, event):
		self._window.withdraw()

	def _on_enter(self, alt: int = 0):
		item: Item | None = self._get_selected_item()
		if item:
			self.parent._thread_router.exec(self._window.withdraw)
			self._on_ok(item, alt)

	def _get_selected_item(self) -> Item | None:
		selection = self._result_listbox.curselection()
		if not selection:
			return None
		try:
			return self._item_list[selection[0]]
		except IndexError:
			return None

	def _on_search_entry_updown(self, event):
		if not self._result_listbox.size():
			return
		if not self._result_listbox.curselection():
			self._result_listbox.selection_set(0)
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
		self._on_enter(0)

	def _on_list_right_click(self, event):
		self._select_item_at_y_pos(event.y)
		self._on_enter(1)

	def _select_item_at_y_pos(self, y: int):
		self._result_listbox.selection_clear(0, tk.END)
		self._result_listbox.selection_set(self._result_listbox.nearest(y))

	def go(self, on_ok: Callable[[Item, int | None], None] = lambda x, y: None):
		self._on_ok = on_ok
		self.show()
		
	def _do_show(self):
		super()._do_show()
		self._search_entry.focus_set()
		self._on_query_entry_type()
		self._search_entry.select_range(0, 'end')
		

	def _on_query_entry_type(self, name=None, index=None, mode=None) -> None:
		self._item_list = self.item_source.search(self._search_query.get())
		self._result_list.set(cast(Any, [str(item) for item in self._item_list]))
		if self._item_list:
			self._result_listbox.select_clear(0, tk.END)
			self._result_listbox.selection_set(0)
		self._result_listbox.see(0)



class Dialog(kwix.Dialog, ModalWindow):
	def __init__(self, parent: Ui, create_dialog: Callable[[DialogBuilder], None]):
		ModalWindow.__init__(self, parent)
		kwix.Dialog.__init__(self, create_dialog)
		self._init_window()
	def _init_window(self):
		self._window.bind('<Return>', cast(Any, self._ok_click))

		frame = ttk.Frame(self._window, padding=8)
		frame.grid(column=0, row=0, sticky='nsew')
		frame.columnconfigure(0, weight=1)
		frame.rowconfigure(0, weight=1)

		data_frame = ttk.Frame(frame)
		data_frame.grid(column=0, row=0, sticky='nsew')

		self.builder = DialogBuilder(data_frame)
		self.create_dialog(self.builder)

		control_frame = ttk.Frame(frame)
		control_frame.rowconfigure(0, weight=1)
		control_frame.columnconfigure(0, weight=1)
		control_frame.grid(column=0, row=1, sticky='nsew')

		ok_button = ttk.Button(control_frame, text=str(ok_text), command=self._ok_click)
		ok_button.grid(column=1, row=0, padx=4)

		cancel_button = ttk.Button(control_frame, text=str(cancel_text), command=self.hide)
		cancel_button.grid(column=2, row=0, padx=4)

	def _ok_click(self, *args):
		self.hide()
		self._on_ok(self.builder.save(self._value))

	def go(self, value: Any | None, on_ok: Callable[[Any], None] = lambda _: None) -> None:
		self._value = value
		self._on_ok = on_ok
		self.builder.load(value)
		self.show()
		





		


class other:

	def _edit_selected_action(self):
		action: Action | None = self._get_selected_action()
		if not action:
			return
		def on_create_dialog(dialog_builder: DialogBuilder):
			action.action_type.create_editor(dialog_builder, action)
		self.show_modal_window(on_create_dialog)

	def show_modal_window(self, on_create_dialog: Callable[[DialogBuilder], None]):
		window = tk.Toplevel(self._root)
		window.geometry("500x500")
		window.columnconfigure(0, weight=1)
		window.rowconfigure(0, weight=1)
		window.transient(self._root)

		frame = ttk.Frame(window, padding=0)
		frame.grid(column=0, row=0, sticky='nsew')

		dialog = DialogBuilder(frame)
		dialog.on_destroy(window.destroy)
		on_create_dialog(dialog)
		
		window.wait_visibility()
		window.grab_set()
		window.focus_set()
		window.wait_window()



	def _forbid_minimize(self):
		try:
			self._root.attributes("-toolwindow", True)
		except:
			pass
		# self._root.attributes('-type', 'dock')


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



class DialogEntry(kwix.DialogEntry):
	def __init__(self, label: ttk.Label, string_var: tk.StringVar):
		self._label = label
		self._string_var = string_var

	def set_title(self, text: str):
		self._label.config(text=text)

	def get_value(self):
		return self._string_var.get()

	def set_value(self, value):
		self._string_var.set(value)

	def on_change(self, func: callable):
		self._string_var.trace_add(
			"write", lambda *args, **kwargs: func(self._string_var.get()))


class DialogBuilder(kwix.DialogBuilder):
	def __init__(self, root_frame: ttk.Frame):
		super().__init__()
		self._root_frame = root_frame
		self._widget_count = 0	

	def create_entry(self, id: str, title: str) -> DialogEntry:
		self._root_frame.columnconfigure(0, weight=1)

		label = ttk.Label(self._root_frame, text=title)
		label.grid(column=0, row=self._widget_count, sticky='ew')
		self._widget_count += 1

		string_var = tk.StringVar(self._root_frame)
		entry = ttk.Entry(self._root_frame, textvariable=string_var)
		entry.grid(column=0, row=self._widget_count, sticky='ew')
		self._widget_count += 1
		if self._widget_count == 2:
			entry.focus_set()

		separator = ttk.Label(self._root_frame, text='')
		separator.grid(
			column=0, row=self._widget_count, sticky='ew')
		self._widget_count += 1

		return cast(DialogEntry, self._add_widget(id, DialogEntry(label, string_var)))
