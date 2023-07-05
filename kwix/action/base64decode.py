


import base64

import pyclip

from kwix import Action, Context
from kwix.impl import BaseAction, BaseActionType, BasePlugin


class Base64DecodeActionType(BaseActionType):
	def __init__(self, context: Context): 
		super().__init__(context, 'base64-decode', 'Base64 decode')
	def create_default_action(self, title: str, description: str | None = None):
		return Base64DecodeAction(self, title, description)


class Base64DecodeAction(BaseAction):
	def _run(self):
		pyclip.copy(base64.b64decode(pyclip.paste()))


class Plugin(BasePlugin):
	def add_action_types(self):
		self.action_type = Base64DecodeActionType(self.context)
		self.context.action_registry.add_action_type(self.action_type)
	def add_actions(self):
		def create_actions() -> list[Action]:
			return [ # todo quick hack
					Base64DecodeAction(self.action_type, 'Base64 decode', 'decode base64')
			]
		self.add_default_actions('base64-decode', create_actions)