"""
Read & write entry_points.txt files

Visit <https://github.com/jwodder/entry-points-txt> for more information.
"""

__version__      = '0.1.0.dev1'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'entry-points-txt@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/entry-points-txt'

from   importlib import import_module
from   io        import StringIO
from   keyword   import iskeyword
import re
from   typing    import Any, Dict, IO, Iterable, NamedTuple, Optional, Tuple

class EntryPoint(NamedTuple):
    group:  str
    name:   str
    module: str
    object: Optional[str]
    extras: Tuple[str, ...]

    def load(self) -> Any:
        obj = import_module(self.module)
        if self.object is not None:
            for attr in self.object.split('.'):
                obj = getattr(obj, attr)
        return obj

    def to_line(self) -> str:
        s = f'{self.name} = {self.module}'
        if self.object is not None:
            s += f':{self.object}'
        if self.extras:
            s += f' [{",".join(self.extras)}]'
        return s


EntryPointSet = Dict[str, Dict[str, EntryPoint]]

GROUP_RGX = re.compile(r'\w+(?:\.\w+)*')
EXTRA_RGX = re.compile(r'[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?')

def load(fp: IO[str]) -> EntryPointSet:
    eps = {}
    group = None
    for line in fp:
        line = line.strip()
        if not line or line.startswith(('#', ';')):
            continue
        if line.startswith('['):
            if not line.endswith(']'):
                raise ParseError('Group header missing closing bracket')
            group = line[1:-1].strip()
            if not group:
                raise ParseError('Empty group name')
            if not GROUP_RGX.fullmatch(group):
                raise ParseError(f'Invalid group name: {group!r}')
        else:
            if group is None:
                raise ParseError(
                    'Entry point line occurs before any group headers'
                )
            name, eq, spec = line.partition('=')
            if not eq:
                raise ParseError(f"Invalid line (no '='): {line!r}")
            name = name.strip()
            if not name:
                raise ParseError('Empty entry point name')
            pre_bracket, bracket, post_bracket = spec.partition('[')
            module, colon, objname = pre_bracket.strip().partition(':')
            module = module.strip()
            if not module:
                raise ParseError('Empty module name')
            if not _is_dotted_id(module):
                raise ParseError(f'Invalid module name: {module!r}')
            if colon:
                objname = objname.strip()
                if not objname:
                    raise ParseError('Missing object name after colon')
                if not _is_dotted_id(objname):
                    raise ParseError(f'Invalid object name: {objname!r}')
            else:
                objname = None
            if bracket:
                extrastr, cbracket, trail = post_bracket.partition(']')
                if not cbracket:
                    raise ParseError('Extras missing closing bracket')
                if trail.strip():
                    raise ParseError('Trailing characters after extras')
                extras = tuple(e.strip() for e in extrastr.split(','))
                for e in extras:
                    if not EXTRA_RGX.fullmatch(e):
                        raise ParseError(f'Invalid extra: {e!r}')
            else:
                extras = ()
            eps.setdefaut(group, {})[name] = EntryPoint(
                group  = group,
                name   = name,
                module = module,
                object = objname,
                extras = extras,
            )

def loads(s: str) -> EntryPointSet:
    return load(StringIO(s))

def dump(eps: EntryPointSet, fp: IO[str]) -> None:
    raise NotImplementedError

def dumps(eps: EntryPointSet) -> str:
    fp = StringIO()
    dump(eps, fp)
    return fp.getvalue()

def dump_list(eps: Iterable[EntryPoint], fp: IO[str]) -> None:
    raise NotImplementedError

def dumps_list(eps: Iterable[EntryPoint]) -> str:
    fp = StringIO()
    dump_list(eps, fp)
    return fp.getvalue()

def _is_dotted_id(s: str) -> bool:
    return all(p.isidentifier() and not iskeyword(p) for p in s.split('.'))

class Error(Exception):
    pass

class ParseError(Error, ValueError):
    pass
