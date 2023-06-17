
from typing import Any, Sequence

import kwix
from kwix import Action, ActionType, Context


class QuitActionType(ActionType):
	def __init__(self, context: Context):
		ActionType.__init__(self, context, 'kwix.action.quit', 'Quit Kwix')

	def action_from_config(self, value: Any):
		self._assert_config_valid(value)
		return QuitAction(self, value.get('title'), value.get('description'))

	def create_default_actions(self) -> Sequence[Action]:
		return [QuitAction(self, 'quit', 'quit kwix')]


class QuitAction(Action):
	def run(self):
		self.action_type.context.quit()


class Plugin(kwix.Plugin):
	def on_before_run(self):
		action_type = QuitActionType(self.context)
		self.context.action_registry.add_action_type(action_type)
		def create_default_actions():
			return [QuitAction(action_type, 'quit kwix', 'quit kwix descr')]
		self.add_default_actions(action_type.id, create_default_actions)
