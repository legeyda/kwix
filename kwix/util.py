
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
		

def query_match(query: str, *contents: str):
	if not query:
		return True
	for item in contents:
		if item and query.lower() in item.lower():
			return True
	return False



T = TypeVar("T")
class Propty(Generic[T]):
	def __init__(self, default: T = None, on_change: str | bool | Callable[[T], None] = True, private: str | None = None, writeable: bool = True):
		self._default = default
		self._on_change = on_change
		self._private = cast(str, private)
		self._writeable = writeable
	def __set_name__(self, owner: Any, name: str):
		if self._on_change is True:
			self._on_change = '_on_change_' + name
		if not self._private:
			self._private = '_' + name
	def __get__(self, obj: Any, objtype: Any = None) -> T:
		if not obj:
			raise AttributeError("this descriptor is for instances only")
		if not hasattr(obj, self._private):
			return self._default
		return getattr(obj, self._private)
	def __set__(self, obj: Any, new_value: T):
		if not self._writeable:
			raise AttributeError('property for ' + self._private + ' is not writeable')
		old_value: T = self.__get__(obj)
		if old_value is new_value:
			return
		setattr(obj, self._private, new_value)
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
			self._on_change(new_value)

