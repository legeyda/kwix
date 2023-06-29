
from typing import Any, cast

import pynput

import kwix
from kwix import Action, ActionType, Context
from kwix import DialogBuilder, title_text, description_text
from kwix.l10n import _

text_text = _('Text').setup(ru_RU='Текст')

class MachinistActionType(ActionType):
	def __init__(self, context: Context): 
		ActionType.__init__(self, context, 'machinist', 'Machinist')
	def create_default_action(self, title: str | None = None, description: str | None = None, text: str | None = None) -> Action:
		return Machinist(self, title or 'machinist', description or '', '')
	def action_from_config(self, value: Any):
		self._assert_config_valid(value)
		return Machinist(self, value['text'], value.get('title'), value.get('description'))
	def create_editor(self, builder: DialogBuilder) -> None:
		builder.create_entry('text', str(text_text))
		ActionType.create_editor(self, builder)
		def load(value: Any | None):
			if isinstance(value, Machinist):
				builder.widget('text').set_value(cast(Machinist, value).text)
		builder.on_load(load)
		def save(value: Any | None = {}) -> Any:
			if isinstance(value, Machinist):
				value.text = builder.widget('text').get_value()
			else:
				value = Machinist(
					self.context.action_registry.action_types['machinist'], 
					builder.widget('text').get_value(),
					builder.widget('title').get_value(),
					builder.widget('description').get_value())
			return value
		builder.on_save(save)



class Machinist(Action):
	def __init__(self, action_type: ActionType, text: str, title: str | None = None, description: str | None = None):
		title = title or 'type text "' + text + '"'
		Action.__init__(self, action_type, title, description or title)
		self.text = text
	def _match(self, query: str | None = None) -> bool:
		if query and self.text and (query in self.text):
			return True
		return Action._match(self, query)
	def run(self):
		pynput.keyboard.Controller().type(self.text)
	def to_config(self):
		result = Action.to_config(self)
		result['text'] = self.text
		return result


class Plugin(kwix.Plugin):
	def add_action_types(self):
		self.action_type = MachinistActionType(self.context)
		self.context.action_registry.add_action_type(self.action_type)

	def add_actions(self):
		def create_default_actions() -> list[Action]:
			return [ # todo quick hack
					Machinist(self.action_type, '123', 'one two three', 'description of one two three'),
					Machinist(self.action_type, '321')
			]
		self.add_default_actions(self.action_type.id, create_default_actions)