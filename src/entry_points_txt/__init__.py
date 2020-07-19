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

def load(fp: IO[str]) -> EntryPointSet:
    raise NotImplementedError

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

class Error(Exception):
    pass
