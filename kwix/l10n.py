from __future__ import annotations

import locale
from typing import Callable, TypeVar

TypeKey = TypeVar('TypeKey')
TypeValue = TypeVar('TypeValue')
def setdefault(dest: dict[TypeKey, TypeValue], key: TypeKey, supplier: Callable[[], TypeValue]) -> TypeValue:
	if key in dest:
		return dest[key]
	else:
		value = supplier()
		dest[key] = value
		return value


def get_current_locale() -> str:
	return locale.getlocale()[0]


class Text:
	def __init__(self, key: str, default: str | None = None, **l10ns: str):
		self._key: str = key
		self._default: str = default or key
		self._l10ns: dict[str, str] = l10ns

	def __str__(self) -> str:
		return self._l10ns.get(get_current_locale(), self._default)

	def setup(self, default: str | None = None, **kwargs: str) -> Text:
		self._default = default or self._key
		self._l10ns.update(kwargs)
		return self
	
	def apply(self, **values: str) -> str:
		result = str(self)
		for key, value in values.items():
			result = result.replace('{{' + str(key) + '}}', str(value))
		return result



_texts: dict[str, Text] = {}


def gettext(key: str, default: str | None = None, **l10ns: str) -> Text:
	return setdefault(_texts, key, lambda: Text(key, default, **l10ns))


_ = gettext


class Scope:
	def __init__(self, key: str):
		self._key = key

	def gettext(self, key: str) -> Text:
		return gettext(self._key + '.' + key)


_scopes: dict[str, Scope] = {}


def scope(key: str) -> Scope:
	return setdefault(_scopes, key, lambda: Scope(key))


def test():
	from kwix.l10n import _, gettext, scope
	txt = _('Hello').setup(ru_RU='Привет', de_DE='Hallo')
	print(txt)
