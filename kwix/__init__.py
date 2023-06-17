
from __future__ import annotations
from kwix.conf import Conf
from kwix.stor import Stor
from kwix.ui import Window, DialogBuilder
from typing import Any, Callable, cast, Sequence


class Context:
	def __init__(self):
		self._conf: Conf | None = None
		self._window: Window | None = None
		self._action_registry: ActionRegistry | None = None

	def get_conf(self) -> Conf | None:
		return self._conf
	conf = property(get_conf)

	def get_window(self) -> Window | None:
		return self._window
	window = property(get_window)

	def get_action_registry(self) -> ActionRegistry | None:
		return self._action_registry
	action_registry = property(get_action_registry)

	def quit(self) -> None:
		pass


class Plugin:
	def __init__(self, context: Context):
		self.context = context

	def add_default_actions(self, action_type_id: str, supplier: Callable[[], Sequence[Action]]):
		action_type_ids: set[str] = set([action.action_type.id for action in self.context.action_registry.actions])
		if action_type_id not in action_type_ids:
			self.context.action_registry.actions += supplier()

	def on_before_run(self): ...


class ActionType:
	def __init__(self, context: Context, id: str, title: str):
		self.context = context
		self.id = id
		self.title = title

	def action_from_config(self, value: Any) -> Action:
		raise NotImplementedError()

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
	
	def create_editor(self, dialog_builder: DialogBuilder):
		title_entry = dialog_builder.create_entry('title')
		description_entry = dialog_builder.create_entry('description')

		def create_value() -> Action:
			return self.create_default_actions()
		dialog_builder.on_create_value(create_value)

		def update_value(value: Action):
			value.title = title_entry.get_value()
			value.description = description_entry.get_value()
		dialog_builder.on_update_value(update_value)

		def read_value(value: Action):
			title_entry.set_value(value.title)
			description_entry.set_value(value.description)
		dialog_builder.on_read_value(read_value)


class Action:
	def __init__(self, action_type: ActionType, title: str, description: str | None = None):
		self.action_type = action_type
		self.title = title
		self.description = description or title

	def match(self, query: str):
		if not query:
			return True
		return (self.title and (query in self.title)) or (self.description and (query in self.description))

	def run(self) -> None:
		raise NotImplementedError()

	def to_config(self) -> dict[str, Any]:
		return {
			'type': self.action_type.id,
			'title': self.title,
			'description': self.description
		}



class ActionRegistry:
	def __init__(self, stor: Stor):
		self.stor: Stor = stor
		self.action_types: dict[str, ActionType] = {}
		self.actions: list[Action] = []
		self.load()

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
		type_id = value.type
		if type(type_id) != str:
			raise RuntimeError(
				'"type" expected to be str, got ' + type(type_id))
		if type_id not in self.action_types:
			raise RuntimeError('uknown action type id=' + type_id)
		action_type: ActionType = self.action_types[type_id]
		return action_type.action_from_config(value)

	def search(self, query: str | None = None) -> list[Action]:
		if not query:
			return self.actions
		return [x for x in self.actions if x.match(query)]
