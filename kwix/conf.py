from __future__ import annotations

from typing import Any, Callable, Sequence, cast

from kwix.stor import Stor
from kwix.ui import DialogBuilder


class Conf:
	def __init__(self):
		self._scopes: dict[str, Scope] = {}
		self._items: dict[str, Item] = {}
	def _get_data(self) -> dict[Any, Any]:
		...
	def save(self):
		...
	def scope(self, key: str, title: str | None= None) -> Conf:
		if key in self._items:
			raise RuntimeError('cannot create scope "' + key + '": there is item with such key')
		result = self._scopes.get(key)
		if not result:
			result = Scope(self, key, title)
			self._scopes[key] = result
		return result
	def item(self, key: str) -> Item:
		if key in self._scopes:
			raise RuntimeError('cannot create item "' + key + '": there is scope with such key')
		result = self._items.get(key)
		if not result:
			result = Item(self, key)
			self._items[key] = result
		return result
	def create_editor0(self, dialog_builder: DialogBuilder) -> None:
		pass
		# for item in self._items.values():
		# 	entry = dialog_builder.create_entry(item._title)
		# 	dialog_builder.on_read_value(lambda: entry.set_value(item.read()))
		# 	dialog_builder.on_update_value(lambda: item.write(entry.set_value()))
		# for _, scope in self._scopes:
		# 	scope.create_editor(dialog_builder.create_section(item._title))
	def create_editor1(self, dialog_builder: DialogBuilder) -> None:
		pass
		# entries = {}
		# # dialog_builder.list_editor()
		# for key, item in self._all_items_recursive():
		# 	entries[key] = dialog_builder.create_entry(item._title)

		# 	def create_value():
		# 		return {key: item() for (key, item) in entries.items()}
		# 	dialog_builder.on_create_value(create_value)

		# 	def read_value(value):
		# 		pass
		# 	dialog_builder.on_read_value(read_value)

		# 	def update_value(value):
		# 		pass
		# 	dialog_builder.on_update_value(update_value)
	# def _all_items_recursive(self) -> :
	# 	for value in self._items:
	# 		yield value
	# 	for scope in self._scopes:
	# 		yield from scope._all_values_recursive()



class Scope(Conf):
	def __init__(self, parent: Conf, key: str, title: str | None = None):
		super().__init__()
		self._parent = parent
		self._key = key
		self._title = title or key
	def setup(self, title: str | None = None):
		self._title = title or self._key
	def _get_data(self) -> dict[Any, Any]:
		result: Any = super()._get_data().setdefault(self._key, {})
		if not isinstance(result, dict):
			raise RuntimeError('dict expected at scope ' + self._key + ' (' + self._title + ')')
		return cast(dict[Any, Any], result)
	
	def save(self):
		self._parent.save()

	
class StorConf(Conf):
	def __init__(self, stor: Stor):
		Conf.__init__(self)
		self._stor: Stor = stor
	def _get_data(self) -> dict[Any, Any]:
		result = self._stor.data
		if not isinstance(result, dict):
			raise RuntimeError('stor.data expected to be dict)')
		return cast(dict[Any, Any], result)
	def save(self):
		self._stor.save()



class Item:
	def __init__(self, parent: Conf, key: str):
		self._parent = parent
		self._key = key
		self.setup()
	def setup(self, title: str | None = None,
			default: Any = None, mapping: Callable[[Any], Any] | None = None, enum: Sequence[Any] | None = None,
			on_change: Callable[[], None] = None):
		self._title = title or self._key
		self._default = default
		self._mapping = mapping
		self._enum = enum
		self._on_change = on_change
		return self
	def read(self):
		result = self._parent._get_data().get(self._key)
		if self._default and not result:
			result = self._default
		if self._mapping:
			result = self._mapping(result)
		# todo handle enum somehow?
		return result
	def write(self, value: Any):
		data = self._parent._get_data()
		if self._on_change and (not self._key in data or data[self._key] != value):
			self._on_change
		if not self._default or self._default != value:
			data[self._key] = value
		else:
			del data[self._key]
			
