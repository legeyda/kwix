
import kwix
from inspect import isclass

from kwix.impl import BasePlugin
from kwix import Context

class Compound(BasePlugin):
	def __init__(self, context: Context, *wrap: kwix.Plugin):
		super().__init__(context)
		self.wrap = wrap
	def add_action_types(self):
		for plugin in self.wrap:
			plugin.add_action_types()
	def add_actions(self):
		for plugin in self.wrap:
			plugin.add_actions()

class Dispatcher(Compound):
	def __init__(self, context: Context):
		super().__init__(context, *self._load_plugins(context))		
	def _load_plugins(self, context: kwix.Context):
		result: list[kwix.Plugin] = []
		for module in self._discover_modules():
			if not hasattr(module, 'Plugin'):
				continue
			PluginClass = getattr(module, 'Plugin')
			if not isclass(PluginClass):
				continue
			if not issubclass(PluginClass, kwix.Plugin):
				continue
			result.append(PluginClass(context))
		return result
	def _discover_modules(self):
		return [__import__(module_name, fromlist=[None]) for module_name in [
			'kwix.action.machinist', 'kwix.action.quit',
			'kwix.action.base64encode', 'kwix.action.base64decode',
			'kwix.action.add_action']]
