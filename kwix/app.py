
from typing import Any

import pynput

import kwix.impl
import kwix.plugin
import kwix.ui.tk
import kwix.ui.tray
from kwix import Action, ActionRegistry, Context, Item
from kwix.conf import Conf, StorConf
from kwix.impl import BaseItem, BaseItemAlt, FuncItemSource, BaseActionRegistry
from kwix.l10n import _
from kwix.stor import YamlFile
from kwix.util import get_config_dir, get_data_dir

activate_action_text = _('Activate').setup(ru_RU='Выпуолнить', de_DE='Aktivieren')
edit_action_text = _('Edit Action: {{action_title}} ({{action_type_title}})').setup(ru_RU='Редактироваnь действие: {{action_title}} ({{action_type_title}})', de_DE='Aktion Bearbeiten: {{action_title}} ({{action_type_title}})')
delete_action_text = _('Remove Action: {{action_title}} ({{action_type_title}})').setup(ru_RU='Удалить действие: {{action_title}} ({{action_type_title}})', de_DE='Aktion Löschen: {{action_title}} ({{action_type_title}})')






class App(Context):
	def __init__(self):
		pass
	def run(self):
		self.init_conf()
		self.init_action_stor()
		self.init_action_registry()
		self.init_plugins()
		self.init_tray()

	def init_conf(self):
		self._conf = self.create_conf()
	def create_conf(self) -> Conf:
		self.conf_stor = YamlFile(get_config_dir().joinpath('config.yaml'))
		return StorConf(self.conf_stor)
	
	def init_action_stor(self):
		self.action_stor = self.create_action_stor()
		self.action_stor.data = []
	def create_action_stor(self):
		return YamlFile(get_data_dir().joinpath('actions.yaml'))

	def init_action_registry(self):
		self._action_registry = self.create_action_registry()
	def create_action_registry(self) -> ActionRegistry:
		return BaseActionRegistry(self.action_stor)
	
	def init_plugins(self):
		dispatcher = kwix.plugin.Dispatcher(self)
		dispatcher.add_action_types()
		self.action_registry.load()
		dispatcher.add_actions()
	
	def init_tray(self):
		self.tray = kwix.ui.tray.TrayIcon()
		self.tray.on_show = self.activate_action_selector
		self.tray.on_quit = self.quit
		self.tray.run(self.init_ui)

	def init_ui(self):
		self._ui = kwix.ui.tk.Ui()
		self.init_action_selector()
		self.register_global_hotkeys()
		self.ui.run()
		
	def init_action_selector(self):
		self.action_selector = self.ui.selector()
		self.action_selector.title = 'Kwix!!!'
		def edit_action(action: Action) -> None:
			dialog = action.action_type.context.ui.dialog(action.action_type.create_editor)
			def on_dialog_ok(_: Any | None) -> None:
				dialog.destroy()
				self.action_registry.save()
			dialog.go(action, on_dialog_ok)
		def delete_action(action: Action) -> None:
			self.action_registry.actions.remove(action)
			self.action_registry.save()
		def search(query: str) -> list[Item]:
			result: list[Item] = []
			for action in self.action_registry.actions:
				for item in action.search(query):
					alts = list(item.alts)
					def edit_this_action(action: Action = action):
						edit_action(action)
					alts.append(BaseItemAlt(edit_action_text.apply(action_title=action.title, action_type_title=action.action_type.title), edit_this_action))
					def delete_this_action(action: Action = action):
						delete_action(action)
					alts.append(BaseItemAlt(delete_action_text.apply(action_title=action.title, action_type_title=action.action_type.title), delete_this_action))
					result.append(BaseItem(str(item), alts))
			return result
		self.action_selector.item_source = FuncItemSource(search)

	def activate_action_selector(self):
		self.action_selector.go()

	def quit(self):
		self.conf.save()
		self.action_registry.save()
		self.ui.destroy()
		self.tray.stop()
		
		#self.server.stop()

	def register_global_hotkeys(self):
		activate_window_hotkey = self.conf.item('activate_window_hotkey').setup(title = "Activate Window", default = '<ctrl>+;', mapping=str)
		pynput.keyboard.GlobalHotKeys({activate_window_hotkey.read(): self.activate_action_selector}).start()



def main():
	App().run()