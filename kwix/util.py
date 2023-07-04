
import threading
import queue
import logging
import traceback
import pathlib
import os
import collections
import yaml
from collections import UserDict
from typing import Any, cast, Callable, TypeVar, Type, Generic

class ThreadRouter:
	def __init__(self, target_thread: threading.Thread = threading.current_thread()):
		self._target_thread = target_thread
		self._queue = queue.Queue()
	def exec(self, action):
		if threading.current_thread() == self._target_thread:
			action()
		else:
			self._queue.put(action)
	def process(self):
		if threading.current_thread() != self._target_thread:
			raise RuntimeError('wrong thread')
		while True:
			try:
				item = self._queue.get(False)
			except queue.Empty:
				return
			try:
				item()
			except Exception:
				logging.error(traceback.format_exc())
	


	


def get_data_dir() -> pathlib.Path:
	home = pathlib.Path.home()
	if '/' in str(home):
		return home.joinpath('.local', 'share', 'kwix')
	elif '\\' in str(home):
		appdata = os.getenv('APPDATA')
		if appdata:
			return pathlib.Path(appdata, 'kwix')
		else:
			return home.joinpath('AppData', 'kwix')
		


def get_config_dir() -> pathlib.Path:
	home = pathlib.Path.home()
	if '/' in str(home):
		return home.joinpath('.config', 'kwix')
	elif '\\' in str(home):
		appdata = os.getenv('APPDATA')
		if appdata:
			return pathlib.Path(appdata, 'kwix')
		else:
			return home.joinpath('AppData', 'roaming', 'kwix')
		
def get_cache_dir() -> pathlib.Path:
	home = pathlib.Path.home()
	if '/' in str(home):
		return home.joinpath('.cache', 'kwix')
	elif '\\' in str(home):
		appdata = os.getenv('LOCALAPPDATA')
		if appdata:
			return pathlib.Path(appdata, 'kwix')
		else:
			return home.joinpath('AppData', 'kwix')
		


def is_dict(obj):
	return isinstance(obj, (dict, UserDict))



key_mappings: list[dict[str, str]]=[]
key_sets: list[str] = [
	'abcdefghijklmnopqrstuvwxyz',
	'фисвуапршолдьтщзйкыегмцчня']
for key_set in key_sets:
	for other_key_set in key_sets:
		if key_sets is other_key_set:
			continue
		key_mappings.append(dict(zip(list(key_set), list(other_key_set))))
		

def query_match(query: str, *contents: str):
	if not query:
		return True
	for item in contents:
		if item and query.lower() in item.lower():
			return True
	return False



T = TypeVar("T")
class Propty(Generic[T]):
	def __init__(self, 
	      default: T | None = None,
		  on_change: str | bool | Callable[[Any, T], None] = False,
		  private_name: str | None = None,
		  type: Type[T] | None = None,
		  writeable: bool = True,
		  required: bool = False,
		  getter: Callable[[Any], T] | None = None,
		  setter: Callable[[Any, T], None] | None = None):
		self._default = default
		self._on_change = on_change
		self._private_name = cast(str, private_name)
		self._type = type,
		self._writeable = writeable
		self._required = required
		self._getter = getter
		self._setter = setter
	def __set_name__(self, owner: Any, name: str):
		if self._on_change is True:
			self._on_change = '_on_change_' + name
		if not self._private_name:
			self._private_name = '_' + name
	def __get__(self, obj: Any, objtype: Any = None) -> T:
		return self._get(obj, self._required)
	def _get(self, obj: Any, required: bool) -> T:
		if not obj:
			raise AttributeError("Propty is for instances only")
		if self._getter:
			return self._getter(obj)
		if not hasattr(obj, self._private_name):
			if required:
				raise AttributeError('required attr ' + self._private_name + ' not found', obj = obj, name = self._private_name)
			return cast(T, self._default)
		return getattr(obj, self._private_name)
	def __set__(self, obj: Any, new_value: T):
		if not obj:
			raise AttributeError("Propty is for instances only")
		if not self._writeable:
			raise AttributeError('property for ' + self._private_name + ' is not writeable')
		old_value: T = self._get(obj, False)
		if old_value is new_value:
			return
		if self._setter:
			self._setter(obj, new_value)
		else:
			setattr(obj, self._private_name, new_value)
			if self._on_change is False:
				return
		if isinstance(self._on_change, str):
			if not hasattr(obj, self._on_change):
				raise RuntimeError('method ' + self._on_change + ' not found')
			func = getattr(obj, self._on_change)
			if not callable(func):
				raise RuntimeError('attr ' + self._on_change + ' expected to be callable')
			func(new_value)
		elif callable(self._on_change):
			self._on_change(obj, new_value)

