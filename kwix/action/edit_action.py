
from typing import cast, Any

import kwix
from kwix import Action, ActionType, Context, Item, ItemSource
from kwix.l10n import _
from kwix.util import query_match

add_action_text = _('Add Action', ru_RU='Добавить действие', de_DE='Aktion hinzufuegen')
select_action_type_text = _('Select Action Type', ru_RU='Выбор типа действия', de_DE='Aktionstyp auswählen')


class ActionAddActionType(ActionType):
	def __init__(self, context: Context): 
		ActionType.__init__(self, context, 'add-action', str(add_action_text))
	def create_default_action(self, title: str, description: str | None = None) -> Action:
		return ActionAddAction(self, title, description)

class ActionTypeItem(Item):
	def __init__(self, action_type: ActionType):
		super().__init__(action_type.title)
		self.action_type = action_type

class ActionTypeItemSource(ItemSource):
	def __init__(self, action_types: dict[str, ActionType]):
		self.action_types = action_types
	def search(self, query: str) -> list[Item]:
		return [ActionTypeItem(x) for x in self.action_types.values() if query_match(query, x.title)]

class ActionAddAction(Action):
	def run(self):
		selector = self.action_type.context.ui.selector()
		selector.title = str(select_action_type_text)
		selector.item_source = ActionTypeItemSource(self.action_type.context.action_registry.action_types)
		def on_selector_ready(item: Item):
			item = cast(ActionTypeItem, item)
			if item:
				dialog = self.action_type.context.ui.dialog(item.action_type.create_editor)
				def on_dialog_ready(value: Any | None):
					if isinstance(value, Action):
						self.action_type.context.action_registry.actions.append(value)
				dialog.go(None, on_dialog_ready)
			print(item.action_type.title)
		selector.go(on_selector_ready)

class Plugin(kwix.Plugin):
	def add_action_types(self):
		self.action_type = ActionAddActionType(self.context)
		self.context.action_registry.add_action_type(self.action_type)

	def add_actions(self):
		def create_default_actions() -> list[Action]:
			return [ self.action_type.create_default_action(str(add_action_text) + '...') ]
		self.add_default_actions(self.action_type.id, create_default_actions)