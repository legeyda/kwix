import tkinter as tk
from tkinter import ttk
from typing import Callable, Any, cast, Sequence

import pkg_resources
from PIL import Image, ImageTk

import time
import kwix.impl
import kwix
import kwix.ui
from kwix import DialogBuilder, ItemAlt, Item
import kwix.ui.tk
from kwix.util import ThreadRouter
from kwix import Item, ItemSource
from kwix.impl import EmptyItemSource, BaseSelector, ok_text, cancel_text


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
	def destroy(self):
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
	def destroy(self):
		self._window.destroy()



class Selector(ModalWindow, BaseSelector):
	actions = []

	def __init__(self, parent: Ui, item_source: ItemSource = EmptyItemSource()):
		ModalWindow.__init__(self, parent)
		kwix.impl.BaseSelector.__init__(self, item_source)
		self.result: Item | None = None
		self._init_window()

	def _init_window(self):
		self._window.bind('<Return>', cast(Any, lambda x: self._on_enter(0)))
		self._window.bind('<Alt-KeyPress-Return>', cast(Any, lambda x: self._on_enter(1)))
		#self._window.bind('<Ctrl-F10>')

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

	def _on_enter(self, alt_index: int = -1):
		item: Item | None = self._get_selected_item()
		if item:
			alts: list[ItemAlt] = item.alts
			if alt_index >= 0 and alt_index < len(alts):
				self.hide()
				alts[alt_index].execute()

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
		item: Item | None = self._get_selected_item()
		if item:
			alts: list[ItemAlt] = item.alts
			if len(alts) >= 0:
				popup_menu = tk.Menu(self._result_listbox, tearoff=0)
				popup_menu.bind("<FocusOut>", lambda event: popup_menu.destroy())
				for alt in alts:
					def execute(alt: ItemAlt=alt):
						popup_menu.destroy()
						self.hide()						
						alt.execute()						
					popup_menu.add_command(label = str(alt), command = execute)
				popup_menu.tk_popup(event.x_root, event.y_root)
					

	def _select_item_at_y_pos(self, y: int):
		self._result_listbox.selection_clear(0, tk.END)
		self._result_listbox.selection_set(self._result_listbox.nearest(y))

	def go(self, on_ok: Callable[[Item, int | None], Sequence[ItemAlt]] = lambda x, y: []):
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
		self.create_dialog = create_dialog
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
	def destroy(self) -> None:
		return ModalWindow.destroy(self)
		



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
