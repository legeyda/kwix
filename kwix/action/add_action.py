
from __future__ import annotations

from typing import Any, cast

import kwix
from kwix.impl import BaseItem, BaseItemAlt, BaseAction, BaseActionType, BasePlugin, FuncItemSource
from kwix.l10n import _
from kwix.util import query_match

add_action_text = _('Add Action', ru_RU='Добавить действие', de_DE='Aktion hinzufuegen')
select_action_type_text = _('Select Action Type', ru_RU='Выбор типа действия', de_DE='Aktionstyp auswählen')
select_text = _('Select').setup(ru_RU='Выбрать', de_DE='Auswählen')

class ActionType(BaseActionType):
	def __init__(self, context: kwix.Context): 
		BaseActionType.__init__(self, context, 'add-action', str(add_action_text))
	def create_default_action(self, title: str, description: str | None = None) -> Action:
		return Action(self, title, description)

class Action(BaseAction):
	def _run(self):
		selector = self.action_type.context.ui.selector()
		selector.title = str(select_action_type_text)
		def execute(action_type: ActionType) -> None:
			selector.destroy()
			dialog = self.action_type.context.ui.dialog(action_type.create_editor)
			def on_dialog_ready(value: Any | None) -> None:
				dialog.destroy()
				if isinstance(value, Action):
					self.action_type.context.action_registry.actions.append(value)
					self.action_type.context.action_registry.save()
			dialog.go(None, on_dialog_ready)		
		def search(query: str) -> list[kwix.Item]:
			result: list[kwix.Item] = []
			for action_type in self.action_type.context.action_registry.action_types.values():
				def f(action_type: kwix.ActionType = action_type):
					if query_match(query, action_type.id, action_type.title):
						result.append(BaseItem(action_type.title, [BaseItemAlt(select_text, lambda: execute(action_type))]))
				f()
			return result
		selector.item_source = FuncItemSource(search)
		selector.go()

class Plugin(BasePlugin):
	def add_action_types(self):
		self.action_type = ActionType(self.context)
		self.context.action_registry.add_action_type(self.action_type)

	def add_actions(self):
		def create_default_actions() -> list[Action]:
			return [ self.action_type.create_default_action(str(add_action_text) + '...') ]
		self.add_default_actions(self.action_type.id, create_default_actions)