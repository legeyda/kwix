
from __future__ import annotations
from kwix.conf import Conf
from kwix.stor import Stor
from typing import Any, Callable, cast, Sequence
from kwix.l10n import _

title_text = _('Title').setup(ru_RU = 'Название', de_DE='Bezeichnung')
description_text = _('Description').setup(ru_RU = 'Описание', de_DE = 'Beschreibung')
ok_text = _('OK')
cancel_text = _('Cancel').setup(ru_RU='Отмена', de_DE='Abbrechen')

class Item:
	def __init__(self, title: str):
		self._title = title
	def __str__(self):
		return self._title

class ItemSource:
	def search(self, query: str) -> list[Item]:
		return []


class Context:
	def __init__(self):
		self.conf: Conf | None = None
		self.ui: Ui | None = None
		self.action_registry: ActionRegistry | None = None
	def quit(self) -> None:
		pass


class Plugin:
	def __init__(self, context: Context):
		self.context = context

	def add_default_actions(self, action_type_id: str, supplier: Callable[[], Sequence[Action]]):
		action_type_ids: set[str] = set([action.action_type.id for action in self.context.action_registry.actions])
		if action_type_id not in action_type_ids:
			self.context.action_registry.actions += supplier()

	def add_action_types(self): ...
	def add_actions(self): ...



class ActionType:
	def __init__(self, context: Context, id: str, title: str):
		self.context = context
		self.id = id
		self.title = title

	def create_default_action(self, title: str, description: str | None = None) -> Action:
		raise NotImplementedError()

	def action_from_config(self, value: Any) -> Action:
		dic = self._assert_config_valid(value)
		return self.create_default_action(dic['title'], dic.get('description'))

	def _assert_config_valid(self, value: Any) -> dict[Any, Any]:
		if type(value) != dict:
			raise RuntimeError('json must be object, ' + value + ' given')
		value = cast(dict[Any, Any], value)
		if 'type' not in value:
			raise RuntimeError('"type" must be in json object')
		if value.get('type') != self.id:
			raise RuntimeError('wrong type got ' +
							   str(value.get('type')) + ', expected ' + self.id)
		return value
	

	def create_editor(self, builder: DialogBuilder) -> None:
		builder.create_entry('title', str(title_text))
		builder.create_entry('description', str(description_text))
		def load(value: Any | None):
			if isinstance(value, Action):
				builder.widget('title').set_value(value.title)
				builder.widget('description').set_value(value.description)	
		builder.on_load(load)

		def save(value: Any | None) -> Any:
			value = value or {}
			if isinstance(value, Action):
				value.title = builder.widget('title').get_value()
				value.description = builder.widget('description').get_value()
			if isinstance(value, dict):
				value['title'] = builder.widget('title').get_value()
				value['description'] = builder.widget('description').get_value()
			return value
		builder.on_save(save)


class Runnable(Item):
	def __init__(self, action: Action, title: str, func: Callable[[], None]):
		super().__init__(title)
		self.action = action
		self.func = func
	def __call__(self):
		self.func()

class Action:
	def __init__(self, action_type: ActionType, title: str, description: str | None = None):
		self.action_type = action_type
		self.title = title
		self.description = description or title

	def _match(self, query: str | None = None) -> bool:
		if not query:
			return True
		if self.title and (str(query).lower() in str(self.title).lower()):
			return True
		if self.description and (str(query).lower() in str(self.description).lower()):
			return True
		return False

	def search(self, query: str) -> list[Item]:
		return [Runnable(self, self.title, self.run)] if self._match(query) else []

	def run(self) -> None:
		raise NotImplementedError()
	
	def to_config(self) -> dict[str, Any]:
		return {
			'type': self.action_type.id,
			'title': self.title,
			'description': self.description
		}





class ActionRegistry(ItemSource):
	def __init__(self, stor: Stor):
		self.stor: Stor = stor
		self.action_types: dict[str, ActionType] = {}
		self.actions: list[Action] = []

	def load(self):
		self.stor.load()
		self.actions = [self.action_from_config(x) for x in (self.stor.data or [])]

	def save(self) -> None:
		self.stor.data = [action.to_config() for action in self.actions]
		self.stor.save()

	def add_action_type(self, action_type: ActionType) -> None:
		if action_type.id in self.action_types:
			raise RuntimeError('duplicate action type id=' + action_type.id)
		self.action_types[action_type.id] = action_type

	def action_from_config(self, value: Any) -> Action:
		if type(value) != dict:
			raise RuntimeError('dict expected, got ' + type(value))
		value = cast(dict[Any, Any], value)
		if 'type' not in value:
			raise RuntimeError('"type" expected')
		type_id = value['type']
		if type(type_id) != str:
			raise RuntimeError(
				'"type" expected to be str, got ' + type(type_id))
		if type_id not in self.action_types:
			raise RuntimeError('uknown action type id=' + type_id)
		action_type: ActionType = self.action_types[type_id]
		return action_type.action_from_config(value)

	def search(self, query: str) -> list[Item]:
		result: list[Item] = []
		for action in self.actions:
			for runnable in action.search(query):
				result.append(runnable)
		return result






class Ui:
	def selector(self) -> Selector:
		raise NotImplementedError()
	def dialog(self, create_dialog: Callable[[DialogBuilder], None]) -> Dialog:
		raise NotImplementedError()
	def stop(self) -> None:
		raise NotImplementedError()

class Selector:
	def __init__(self, item_source: ItemSource = ItemSource()):
		self.title = 'kwix'
		self.item_source: ItemSource = item_source
	def go(self, on_ok: Callable[[Item, int], None] = lambda x, y: None):
		result = self.item_source.search('')
		return result[0] if len(result)>0 else None
	def destroy(self):
		pass

	
class Dialog:
	def __init__(self, create_dialog: Callable[[DialogBuilder], None]):
		self.title = 'kwix'
		self.create_dialog = create_dialog
	def go(self, value: Any | None, on_ok: Callable[[Any | None], None] = lambda x: None) -> None:
		raise NotImplementedError()
	def destroy(self):
		pass
	

class DialogWidget:
	def get_value(self) -> str:
		raise NotImplementedError()

	def set_value(self, value: str) -> None:
		raise NotImplementedError()

class DialogEntry(DialogWidget):
	pass


class DialogButton:
	def set_title(self, value: str) -> None:
		raise NotImplementedError()

	def on_click(self, func: Callable[[], None]) -> None:
		raise NotImplementedError()


class DialogBuilder:
	def __init__(self):
		self._on_load: list[Callable[[Any | None], None]] = []
		self._on_save: list[Callable[[Any | None], Any]] = []
		self._widgets: dict[str, DialogWidget] = {}

	def create_entry(self, id: str, title: str) -> DialogEntry:
		raise NotImplementedError()
	
	def widget(self, id: str) -> DialogWidget:
		return self._widgets[id]
	
	def _add_widget(self, id: str, widget: DialogWidget) -> DialogWidget:
		self._widgets[id] = widget
		return widget

	def on_load(self, func: Callable[[Any | None], None]):
		self._on_load.append(func)

	def load(self, value: Any | None):
		for func in self._on_load: func(value)

	def on_save(self, func: Callable[[Any | None], Any]):
		self._on_save.append(func)

	def save(self, value: Any) -> Any | None:
		for func in self._on_save: value = func(value)
		return value
