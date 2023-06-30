
from kwix import Context, Action, ActionRegistry, ItemSource, Item, Runnable
from kwix.stor import YamlFile
from kwix.util import get_config_dir, get_data_dir
import pynput
from kwix.conf import StorConf, Conf
import kwix.ui.tk
import kwix.plugin
from typing import cast
import kwix.ui.tray
from typing import Any, cast

from kwix.l10n import _

edit_action_text = _('Edit Action').setup(ru_RU='Редактироваь действие', de_DE='Aktion Bearbeiten')

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
		self.conf = self.create_conf()
	def create_conf(self) -> Conf:
		self.conf_stor = YamlFile(get_config_dir().joinpath('config.yaml'))
		return StorConf(self.conf_stor)
	
	def init_action_stor(self):
		self.action_stor = self.create_action_stor()
		self.action_stor.data = []
	def create_action_stor(self):
		return YamlFile(get_data_dir().joinpath('actions.yaml'))

	def init_action_registry(self):
		self.action_registry = self.create_action_registry()
	def create_action_registry(self) -> ActionRegistry:
		return ActionRegistry(self.action_stor)
	
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
		self.ui = kwix.ui.tk.Ui()
		self.action_selector = self.ui.selector()
		self.action_selector.title = 'Kwix!!!'
		self.action_selector.item_source = cast(ItemSource, self.action_registry)
		self.register_global_hotkeys()
		self.ui.run()
		
		#self.server = kwix.server.create_server(self)
		#self.server.start()
		#self.init_window()

	def quit(self):
		self.conf.save()
		self.action_registry.save()
		self.ui.stop()
		self.tray.stop()
		
		#self.server.stop()

	def register_global_hotkeys(self):
		activate_window_hotkey = self.conf.item('activate_window_hotkey').setup(title = "Activate Window", default = '<ctrl>+;', mapping=str)
		pynput.keyboard.GlobalHotKeys({activate_window_hotkey.read(): self.activate_action_selector}).start()

	def activate_action_selector(self):
		def on_ready(result: Item, alt: int):
			if not isinstance(result, Runnable):
				return
			runnable = cast(Runnable, result)
			if 1 == alt:
				dialog = self.ui.dialog(runnable.action.action_type.create_editor)
				dialog.title = str(edit_action_text)
				dialog.go(runnable.action)
			else:
				cast(Runnable, result).func()
		self.action_selector.go(on_ready)


	# def init_window(self):
	# 	self._window = self.create_window()
	# 	self.init_plugins()
	# 	self._window.run()

	# def create_window(self):
	# 	return kwix.ui.tk.Selector(self.action_registry)
	


def main():
	App().run()