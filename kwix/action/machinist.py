
from typing import Any, cast

import pynput

from kwix import Context, Action, ActionType
from kwix import DialogBuilder
from kwix.l10n import _
from kwix.impl import BaseActionType, BaseAction, BasePlugin
from kwix.util import query_match

text_text = _('Text').setup(ru_RU='Текст')

class MachinistActionType(BaseActionType):
	def __init__(self, context: Context): 
		BaseActionType.__init__(self, context, 'machinist', 'Machinist')
	def create_default_action(self, title: str, description: str | None = None, text: str | None = None) -> Action:
		return Machinist(self, title, description or '', '')
	def action_from_config(self, value: Any):
		self._assert_config_valid(value)
		return Machinist(self, value['text'], value.get('title'), value.get('description'))
	def create_editor(self, builder: DialogBuilder) -> None:
		builder.create_entry('text', str(text_text))
		super().create_editor(builder)
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



class Machinist(BaseAction):
	def __init__(self, action_type: ActionType, text: str, title: str | None = None, description: str | None = None):
		title = title or 'type text "' + text + '"'
		BaseAction.__init__(self, action_type, title, description or title)
		self.text = text
	def _match(self, query: str) -> bool:
		if query_match(query, self.text):
			return True
		return BaseAction._match(self, query)
	def _run(self):
		pynput.keyboard.Controller().type(self.text)
	def to_config(self):
		result = BaseAction.to_config(self)
		result['text'] = self.text
		return result


class Plugin(BasePlugin):
	def add_action_types(self):
		self.action_type = MachinistActionType(self.context)
		self.context.action_registry.add_action_type(self.action_type)