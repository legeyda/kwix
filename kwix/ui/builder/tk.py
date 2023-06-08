

import tkinter as tk
from tkinter import ttk


import kwix.logic



class Entry(kwix.logic.DialogEntry):
	def __init__(self, string_var: tk.StringVar):
		self._string_var = string_var
	def get_text(self):
		return self._string_var.get()
	def set_text(self, value):
		self._string_var.set(value)

class DialogBuilder(kwix.logic.DialogBuilder):
	def __init__(self, root: ttk.Frame):
		self._root = root
		self._root.columnconfigure(0, weight=1)
		self._widget_count = 0
		
		
	def add_entry(self, title: str, value: str = None, on_change = None) -> Entry:
		label = ttk.Label(self._root, text=title)
		label.grid(column=0, row=self._widget_count, sticky='ew')
		self._widget_count+=1

		string_var = tk.StringVar(self._root, value='helllll')
		string_var.set('hhhhh')
		if on_change:
			string_var.trace_add("write", on_change)
		entry = ttk.Entry(self._root, textvariable=string_var)
		entry.grid(column=0, row=self._widget_count, sticky='ew')
		self._widget_count += 1
		if self._widget_count == 2:
			entry.focus_set()
		
		label = ttk.Label(self._root, text='')
		label.grid(column=0, row=self._widget_count, sticky='ew')
		self._widget_count+=1

		return Entry(string_var)
	
	def on_create_value(self, func):
		self._create_value = func
	def on_update_value(self, func):
		self._update_value = func
	def on_read_value(self, func):
		self._read_value = func

	def create_value(self) -> kwix.logic.ActionType:
		return self._create_value()
	def update_value(self, value: kwix.logic.ActionType):
		return self._update_value(value)
	def read_value(self, value: kwix.logic.ActionType):
		return self._read_value(value)