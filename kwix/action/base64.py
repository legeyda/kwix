


from kwix.action import ActionType, action_type_registry, Action
import base64
from kwix import Context

class Base64EncodeActionType(ActionType):
	def __init__(self): 
		ActionType.__init__(self, 'base64-encode', 'Base-64 encode')
	def new_instance(self, title: str = None, description: str = None):
		return Base64EncodeAction(self, title, description)
	def action_from_config(self, value: dict):
		self._assert_config_valid(value)
		return self.new_instance(value['text'], value.get('title'), value.get('description'))
	def create_editor(self, dialog_builder: kwix.ui.DialogBuilder):
		title_entry = dialog_builder.create_entry('title')
		description_entry = dialog_builder.create_entry('description')

		def create_value():
			return Base64EncodeAction(text_entry.get_value(), title_entry.get_value(), description_entry.get_value())
		dialog_builder.on_create_value(create_value)

		def update_value(value: Base64EncodeAction):
			value.title = title_entry.get_value()
			value.description = description_entry.get_value()
		dialog_builder.on_update_value(update_value)

		def read_value(value: Base64EncodeAction):
			title_entry.set_value(value.title)
			description_entry.set_value(value.description)
		dialog_builder.on_read_value(read_value)


base64ActionType = Base64EncodeActionType()
action_type_registry.add(base64ActionType)


class Base64EncodeAction(Action):
	def __init__(self, title: str, description: str = None):
		Action.__init__(self, base64ActionType, title, description)
	def match(self, query: str):
		return Action.match(self, query) or (self.text and (query in self.text))
	def run(self, context: Context):
		pynput.keyboard.Controller().type(self.text)
	def to_config(self):
		return {
			'type': self.action_type.id,
			'text': self.text,
			'title': self.title,
			'description': self.description
		}


class Plugin(kwix.Plugin):
	def on_before_run(self, context: Context):
		...