
from typing import Any

import pynput

import kwix
from kwix import Action, ActionType, Context
from kwix.ui import DialogBuilder, DialogEntry


class MachinistActionType(ActionType):
	def __init__(self, context: Context): 
		ActionType.__init__(self, context, 'machinist', 'Machinist')
	def action_from_config(self, value: Any):
		self._assert_config_valid(value)
		return Machinist(self, value['text'], value.get('title'), value.get('description'))
	def create_editor(self, dialog_builder: DialogBuilder):
		text_entry: DialogEntry = dialog_builder.create_entry('text')
		title_entry = dialog_builder.create_entry('title')
		description_entry = dialog_builder.create_entry('description')

		def create_value():
			return Machinist(self, text_entry.get_value(), title_entry.get_value(), description_entry.get_value())
		dialog_builder.on_create_value(create_value)

		def update_value(value: Machinist):
			value.title = title_entry.get_value()
			value.text = text_entry.get_value()
			value.description = description_entry.get_value()
		dialog_builder.on_update_value(update_value)

		def read_value(value: Machinist):
			text_entry.set_value(value.text)
			title_entry.set_value(value.title)
			description_entry.set_value(value.description)
		dialog_builder.on_read_value(read_value)

class Machinist(Action):
	def __init__(self, action_type: ActionType, text: str, title: str | None = None, description: str | None = None):
		title = title or 'type text "' + text + '"'
		Action.__init__(self, action_type, title, description or title)
		self.text = text
	def match(self, query: str):
		return Action.match(self, query) or (self.text and (query in self.text))
	def run(self):
		pynput.keyboard.Controller().type(self.text)
	def to_config(self):
		return {
			'type': self.action_type.id,
			'text': self.text,
			'title': self.title,
			'description': self.description
		}


class Plugin(kwix.Plugin):
	def on_before_run(self):
		action_type = MachinistActionType(self.context)
		self.context.action_registry.add_action_type(action_type)
		def create_default_actions() -> list[Action]:
			return [ # todo quick hack
					Machinist(action_type, '123', 'one two three', 'description of one two three'),
					Machinist(action_type, '321')
			]
		self.add_default_actions(action_type.id, create_default_actions)
