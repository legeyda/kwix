from __future__ import annotations

from typing import Callable, Type, TypeVar

TypeKey = TypeVar('TypeKey')
TypeValue = TypeVar('TypeValue')


def setdefault(dest: dict[Type[TypeKey], Type[TypeValue]], key: Type[TypeKey], supplier: Callable[[], Type[TypeValue]]) -> TypeValue:
	if key in dest:
		return dest[key]
	else:
		value = supplier()
		dest[key] = value
		return value


def get_current_locale() -> str:
	return ''


class Text:
	def __init__(self, key: str, default: str | None = None, **l10ns: str):
		self._key: str = key
		self._default: str = default or key
		self._l10ns: dict[str, str] = l10ns

	def __str__(self) -> str:
		return self._l10ns.get(get_current_locale(), self._default)

	def default(self, default: str):
		return Text(self._key, default, **self._l10ns)

	def setup(self, **kwargs: str):
		l10ns: dict[str, str] = {}
		l10ns.update(self._l10ns)
		l10ns.update(kwargs)
		return Text(self._key, self._default, **l10ns)


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
	from kwix.l10n import gettext, scope, _
	txt = _('Hello').setup(ru_RU='Привет', de_DE='Hallo')
	print(txt)
