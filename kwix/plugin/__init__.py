
import kwix
from inspect import isclass



class Dispatcher(kwix.Plugin):
	def __init__(self, context: kwix.Context):
		kwix.Plugin.__init__(self, context)
		self._load_plugins()
	def _load_plugins(self):
		self._plugins = []
		for module in self._discover_modules():
			if not hasattr(module, 'Plugin'):
				continue
			PluginClass = getattr(module, 'Plugin')
			if not isclass(PluginClass):
				continue
			if not issubclass(PluginClass, kwix.Plugin):
				continue
			self._plugins.append(PluginClass(self.context))
	def _discover_modules(self):
		return [__import__(module_name, fromlist=[None]) for module_name in ['kwix.action.machinist', 'kwix.action.quit']]
	def on_before_run(self):
		for plugin in self._plugins:
			plugin.on_before_run()

