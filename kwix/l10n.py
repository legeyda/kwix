






def get_current_locale():
    pass

current_locale = get_cur


class Scope:
    def __init__(self, key: str):
        self._key = key
    def gettext(self, key) -> LocalizedString:
        return gettext(self._key + '.' + key)

_scopes = {}

def scope(key: str) -> Scope:
    result = _scopes.get(key)
    if not result:
        result = Scope(key)
        _scopes[key] = result
    return result




class Text:
    def __init__(self, key: str, default: str = None):
        self._key = key
        self._default = default or key
        self._l10ns = {}
    def __str__(self):
        return self._l10ns.get(current_locale, self._default)
    def default(self, default = None):
        self._default = default
        return self
    def set(self, **kwargs: dict[str, str]):
        self._l10ns.update(kwargs)
        return self

_texts = {}

def gettext(key: str):
    result = _strings.get(key)
    if not result:
        result = Text(key)
        _texts[key] = result
    return result

_ = gettext



def test():
    import kwix.l10n
    scope = kwix.l10n.scope('action.machinist')
    str(scope.gettext('text').set(
        en_US='text',
        ru_RU='текст',
        de_DE='Texte'))
