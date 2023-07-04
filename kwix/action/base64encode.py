


import base64

import pyclip

from kwix import Action, Context
from kwix.impl import BaseAction, BaseActionType, BasePlugin


class Base64EncodeActionType(BaseActionType):
	def __init__(self, context: Context): 
		super().__init__(context, 'base64-encode', 'Base64 encode')
	def create_default_action(self, title: str, description: str | None = None):
		return Base64EncodeAction(self, title, description)

class Base64EncodeAction(BaseAction):
	def _run(self):
		pyclip.copy(base64.b64encode(pyclip.paste()))


class Plugin(BasePlugin):
	def add_action_types(self):
		self.action_type = Base64EncodeActionType(self.context)
		self.context.action_registry.add_action_type(self.action_type)

	def add_actions(self):
		def create_actions() -> list[Action]:
			return [ # todo quick hack
					Base64EncodeAction(self.action_type, 'Base64 encode', 'encode base64')
			]
		self.add_default_actions('base64-encode', create_actions)