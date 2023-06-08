
from kwix.logic import Action
import pynput
from kwix.logic import Context
import json
from kwix.logic import ActionType
import kwix.logic





class Machinist(Action):
	def __init__(self, text: str, title: str = None, description: str = None):
		title = title or 'type text "' + text + '"'
		Action.__init__(self, MachinistType(), title, description or title)
		self.text = text
	def match(self, query: str):
		return Action.match(self, query) or (self.text and (query in self.text))
	def go(self, context: Context):
		context.window.hide()
		pynput.keyboard.Controller().type(self.text)

class MachinistType(ActionType):
	def __init__(self): 
		ActionType.__init__(self, 'machinist', 'Machinist');
	def from_json(self, value: dict):
		self._assert_json_valid(value)
		return Machinist(value['text'], value.get('title'), value.get('description'))
	def create_editor(self, dialog_builder: kwix.logic.DialogBuilder):
		text_entry = dialog_builder.add_entry('text')
		title_entry = dialog_builder.add_entry('title')
		description_entry = dialog_builder.add_entry('description')

		def create_value():
			return Machinist(text_entry.get_text(), title_entry.get_text(), description_entry.get_text())
		dialog_builder.on_create_value(create_value)

		def update_value(value: Machinist):
			value.title = title_entry.get_text()
			value.text = text_entry.get_text()
			value.description = description_entry.get_description()
		dialog_builder.on_update_value(update_value)

		def read_value(value: Machinist):
			text_entry.set_text(value.text)
			title_entry.set_text(value.title)
			description_entry.set_text(value.description)
		dialog_builder.on_read_value(read_value)

kwix.logic.action_type_registry.add(MachinistType())