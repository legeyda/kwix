from typing import Any, Callable

class Window:
	def show(self): pass
	def hide(self): pass



class DialogEntry:
	def get_value(self) -> str: ...
	def set_value(self, value: str): ...


class DialogBuilder:
	def __init__(self):
		self._create_value = None
		self._update_value_list: list[Any] = []
		self._read_value_list: list[Any] = []
	def create_entry(self, title: str, on_change: Callable[[], None] = lambda: None) -> DialogEntry:
		raise NotImplementedError()
	def on_create_value(self, func: Callable[[], Any]) -> Any | None:
		self._create_value = func
	def on_update_value(self, func: Callable[[Any], None]) -> None:
		self._update_value_list.append(func)
	def on_read_value(self, func: Callable[[Any], None]) -> None:
		self._read_value_list.append(func)

	def create_value(self) -> Any:
		"""read ui and create value"""
		if self._create_value:
			return self._create_value()
	def update_value(self, value: Any):
		"""read ui and update value"""
		for func in self._update_value_list: func(value)
	def read_value(self, value: Any):
		"""read ui and update dialog"""
		for func in self._read_value_list: func(value)

