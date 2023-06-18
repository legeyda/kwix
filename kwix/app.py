
from kwix import Context, ActionRegistry
from kwix.stor import YamlFile
from kwix.util import get_config_dir, get_data_dir
import pynput
from kwix.conf import StorConf, Conf
import kwix.ui.tk
import kwix.plugin

import kwix.ui.tray



class App(Context):
	def __init__(self):
		pass
	def run(self):
		self.init_conf()
		self.init_action_stor()
		self.init_action_registry()
		self.tray = kwix.ui.tray.TrayIcon()
		self.tray.on_show = self.toggle_window
		self.tray.on_quit = self.quit
		self.tray.run(self.after_tray)

	def init_conf(self):
		self._conf = self.create_conf()
	def create_conf(self) -> Conf:
		self._conf_stor = YamlFile(get_config_dir().joinpath('config.yaml'))
		return StorConf(self._conf_stor)
	
	def init_action_stor(self):
		self._action_stor = self.create_action_stor()
		self._action_stor.data = []
	def create_action_stor(self):
		return YamlFile(get_data_dir().joinpath('actions.yaml'))

	def init_action_registry(self):
		self._action_registry = self.create_action_registry()
	def create_action_registry(self) -> ActionRegistry:
		return ActionRegistry(self._action_stor)


	def toggle_window(self):
		if not self.window.is_visible():
			self.window.show()
		else:
			self.window.hide()
	def quit(self):
		self._conf.save()
		self._action_registry.save()
		self.window.quit()
		self.tray.stop()
		
		#self.server.stop()
	def after_tray(self):
		self.register_global_hotkeys()
		
		#self.server = kwix.server.create_server(self)
		#self.server.start()
		self.init_window()
	def register_global_hotkeys(self):
		activate_window_hotkey = self._conf.item('activate_window_hotkey').setup(title = "Activate Window", default = '<ctrl>+;', mapping=str)
		pynput.keyboard.GlobalHotKeys({activate_window_hotkey.read(): self.toggle_window}).start()
	def init_window(self):
		self._window = self.create_window()
		self.on_before_run()
		self._window.run()
	def create_window(self):
		return kwix.ui.tk.Window(self.action_registry)
	def on_before_run(self):
		dispatcher = kwix.plugin.Dispatcher(self)
		dispatcher.register_action_types()
		self.action_registry.load()
		dispatcher.add_actions()
	


def main():
	App().run()