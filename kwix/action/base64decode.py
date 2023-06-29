


import base64
from typing import Any

import pyclip

import kwix
from kwix import Action, ActionType, Context
import binascii

class Base64DecodeActionType(ActionType):
	def __init__(self, context: Context): 
		ActionType.__init__(self, context, 'base64-decode', 'Base64 decode')
	def create_default_action(self, title: str, description: str | None = None):
		return Base64DecodeAction(self, title, description)


class Base64DecodeAction(Action):
	def _match(self, query: str | None = None) -> bool:
		# x = pyclip.paste()
		# if not x:
		# 	return False
		return super()._match(query)
	def run(self):
		pyclip.copy(base64.b64decode(pyclip.paste()))


class Plugin(kwix.Plugin):
	def add_action_types(self):
		self.action_type = Base64DecodeActionType(self.context)
		self.context.action_registry.add_action_type(self.action_type)

	def add_actions(self):
		def create_actions() -> list[Action]:
			return [ # todo quick hack
					Base64DecodeAction(self.action_type, 'Base64 decode', 'decode base64')
			]
		self.add_default_actions('base64-decode', create_actions)