

class Logic:
	def __init__(self, actions=[]):
		self._actions = actions
	def action_search(self, query: str = None):
		if not query: 
			return self._actions
		return [x for x in self._actions if x.match(query)]

class Window:
	def show(): pass
	def hide():	pass


class Context:
	def __init__(self, logic: Logic, window: Window):
		self.logic = logic
		self.window = window





class DialogEntry:
	def get_text(self): ...
	def set_text(self, value: str): ...

class DialogBuilder():
	def add_entry(self, title: str, on_change = lambda *args: ...) -> DialogEntry: ...
	def create_value(self): ...
	def update_value(self, value): ...
	def read_value(self, value): ...





class ActionType:
	def __init__(self, id: str, title: str):
		self.id = id
		self.title = title
	def instantiate_from_json(self):
		pass
	def _assert_json_valid(self, value):
		if type(value) != dict:
			raise RuntimeError('json must be object, ' + value + ' given')
		if 'type' not in value:
			raise RuntimeError('"type" must be in json object')
		if value['type'] != self.id:
			raise RuntimeError('wrong type got ' + value['type'] + ', expected ' + self.id)
	def create_editor(self, dialog_builder: DialogBuilder):
		pass

	

class Action:
	def __init__(self, action_type: ActionType, title: str, description: str = None):
		if self is Action: raise 'abc'
		self.action_type = action_type
		self.title = title
		self.description = description or title
	def match(self, query: str):
		if not query:
			return True
		return (self.title and (query in self.title)) or (self.description and (query in self.description))
	def go(self, context: Context):
		pass
	def memo(self):
		pass




class _ActionTypeRegistry():
	def __init__(self):
		self._data = {}
	def add(self, value: ActionType):
		if value.id in self._data:
			raise RuntimeError('duplicate action type id=' + value.id)
		self._data[value.id] = value
	def get_all(self):
		return dict(self._data)


action_type_registry = _ActionTypeRegistry()


