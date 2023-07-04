
from kwix import Action, Context
from kwix.impl import BaseAction, BaseActionType, BasePlugin


class QuitActionType(BaseActionType):
	def __init__(self, context: Context):
		super().__init__(context, 'kwix.action.quit', 'Quit Kwix')

	def create_default_action(self, title: str, description: str | None = None) -> Action:
		return QuitAction(self, title, description)

class QuitAction(BaseAction):
	def _run(self):
		self.action_type.context.quit()

class Plugin(BasePlugin):
	def add_action_types(self):
		self.action_type = QuitActionType(self.context)
		self.context.action_registry.add_action_type(self.action_type)
	def add_actions(self):
		def create_default_actions():
			return [QuitAction(self.action_type, 'quit kwix', 'quit kwix descr')]
		self.add_default_actions(self.action_type.id, create_default_actions)