"""
Read & write entry_points.txt files

``entry-points-txt`` provides functions for reading & writing
``entry_points.txt`` files according to `the spec`_.  That is the one thing it
does, and it endeavors to do it well.

.. _the spec: https://packaging.python.org/specifications/entry-points/

Visit <https://github.com/jwodder/entry-points-txt> for more information.
"""

__version__ = "0.2.0"
__author__ = "John Thorvald Wodder II"
__author_email__ = "entry-points-txt@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/entry-points-txt"

__all__ = [
    "EntryPoint",
    "EntryPointSet",
    "ParseError",
    "dump",
    "dump_list",
    "dumps",
    "dumps_list",
    "load",
    "loads",
]

from importlib import import_module
from io import StringIO
from keyword import iskeyword
import re
from typing import Any, Dict, IO, Iterable, NamedTuple, Optional, Tuple
from warnings import warn


class EntryPoint(NamedTuple):
    """A representation of an entry point as a namedtuple."""

    #: The name of the entry point group (e.g., ``"console_scripts"``)
    group: str
    #: The name of the entry point
    name: str
    #: The module portion of the attribute reference (the part before the
    #: colon)
    module: str
    #: The attribute/object portion of the attribute reference (the part after
    #: the colon), or `None` if not specified
    #:
    #: .. versionadded:: 0.2.0
    attr: Optional[str]
    #: Extras required for the entry point
    extras: Tuple[str, ...]

    @property
    def object(self) -> Optional[str]:
        """
        Alias for `attr`

        .. deprecated:: 0.2.0
            Use `attr` instead
        """
        warn(
            "EntryPoint.object is deprecated.  Use EntryPoint.attr instead.",
            DeprecationWarning,
        )
        return self.attr

    def load(self) -> Any:
        """Returns the object referred to by the entry point"""
        obj = import_module(self.module)
        if self.attr is not None:
            for attr in self.attr.split("."):
                obj = getattr(obj, attr)
        return obj

    def to_line(self) -> str:
        """
        Returns the representation of the entry point as a line in
        :file:`entry_points.txt`, i.e., a line of the form ``name =
        module:attr [extras]``
        """
        s = f"{self.name} = {self.module}"
        if self.attr is not None:
            s += f":{self.attr}"
        if self.extras:
            s += f' [{",".join(self.extras)}]'
        return s


EntryPointSet = Dict[str, Dict[str, EntryPoint]]

GROUP_RGX = re.compile(r"\w+(?:\.\w+)*")
EXTRA_RGX = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?")


def load(fp: IO[str]) -> EntryPointSet:
    """
    Parse a file-like object as an :file:`entry_points.txt`-format file and
    return the results.  The parsed entry points are returned in a `dict`
    mapping each group name to a `dict` mapping each entry point name to an
    `EntryPoint` object.

    For example, the following input:

    .. code-block:: ini

        [console_scripts]
        foo = package.__main__:main
        bar = package.cli:klass.attr

        [thingy.extension]
        quux = package.thingy [xtr]

    would be parsed as:

    .. code-block:: python

        {
            "console_scripts": {
                "foo": EntryPoint(
                    group="console_scripts",
                    name="foo",
                    module="package.__main__",
                    attr="main",
                    extras=(),
                ),
                "bar": EntryPoint(
                    group="console_scripts",
                    name="bar",
                    module="package.cli",
                    attr="klass.attr",
                    extras=(),
                ),
            },
            "thingy.extension": {
                "quux": EntryPoint(
                    group="thingy.extension",
                    name="quux",
                    module="package.thingy",
                    attr=None,
                    extras=("xtr",),
                ),
            },
        }
    """

    eps: EntryPointSet = {}
    group = None
    for line in fp:
        line = line.strip()
        if not line or line.startswith(("#", ";")):
            continue
        if line.startswith("["):
            if not line.endswith("]"):
                raise ParseError("Group header missing closing bracket")
            group = line[1:-1].strip()
            if not group:
                raise ParseError("Empty group name")
            if not GROUP_RGX.fullmatch(group):
                raise ParseError(f"Invalid group name: {group!r}")
        else:
            if group is None:
                raise ParseError("Entry point line occurs before any group headers")
            name, eq, spec = line.partition("=")
            if not eq:
                raise ParseError(f"Invalid line (no '='): {line!r}")
            name = name.strip()
            if not name:
                raise ParseError("Empty entry point name")
            pre_bracket, bracket, post_bracket = spec.partition("[")
            objname: Optional[str]
            module, colon, objname = pre_bracket.strip().partition(":")
            module = module.strip()
            if not module:
                raise ParseError("Empty module name")
            if not _is_dotted_id(module):
                raise ParseError(f"Invalid module name: {module!r}")
            if colon:
                objname = objname.strip()
                if not objname:
                    raise ParseError("Missing attribute name after colon")
                if not _is_dotted_id(objname):
                    raise ParseError(f"Invalid attribute name: {objname!r}")
            else:
                objname = None
            if bracket:
                extrastr, cbracket, trail = post_bracket.partition("]")
                if not cbracket:
                    raise ParseError("Extras missing closing bracket")
                if trail.strip():
                    raise ParseError("Trailing characters after extras")
                extrastr = extrastr.strip()
                if extrastr:
                    extras = tuple(e.strip() for e in extrastr.split(","))
                    for e in extras:
                        if not EXTRA_RGX.fullmatch(e):
                            raise ParseError(f"Invalid extra: {e!r}")
                else:
                    extras = ()
            else:
                extras = ()
            eps.setdefault(group, {})[name] = EntryPoint(
                group=group,
                name=name,
                module=module,
                attr=objname,
                extras=extras,
            )
    return eps


def loads(s: str) -> EntryPointSet:
    """Like `load()`, but reads from a string instead of a filehandle"""
    return load(StringIO(s))


def dump(eps: EntryPointSet, fp: IO[str]) -> None:
    """
    Write a collection of entry points (in the same structure as returned by
    `load()`) to a file-like object in :file:`entry_points.txt` format.  A
    `ValueError` is raised and nothing is written if the group or name key
    under which an `EntryPoint` is located does not match its ``group`` or
    ``name`` attribute.
    """
    print(dumps(eps), file=fp, end="")


def dumps(eps: EntryPointSet) -> str:
    """
    Like `dump()`, but returns a string instead of writing to a filehandle
    """
    s = ""
    first = True
    for group, items in eps.items():
        if not items:
            continue
        if first:
            first = False
        else:
            s += "\n"
        s += f"[{group}]\n"
        for name, ep in items.items():
            if ep.group != group:
                raise ValueError(
                    f"Group mismatch: entry point with group {ep.group!r}"
                    f" placed under {group!r} dict"
                )
            if ep.name != name:
                raise ValueError(
                    f"Name mismatch: entry point with name {ep.name!r} placed"
                    f" under key {name!r}"
                )
            s += ep.to_line() + "\n"
    return s


def dump_list(eps: Iterable[EntryPoint], fp: IO[str]) -> None:
    """
    Write an iterable of entry points to a file-like object in
    :file:`entry_points.txt` format.  If two or more entry points have the same
    group & name, only the last one will be output.
    """
    print(dumps_list(eps), file=fp, end="")


def dumps_list(eps: Iterable[EntryPoint]) -> str:
    """
    Like `dump_list()`, but returns a string instead of writing to a filehandle
    """
    epset: EntryPointSet = {}
    for ep in eps:
        epset.setdefault(ep.group, {})[ep.name] = ep
    return dumps(epset)


def _is_dotted_id(s: str) -> bool:
    """
    Tests whether the given string is a valid dotted sequence of Python
    identifiers
    """
    return all(p.isidentifier() and not iskeyword(p) for p in s.split("."))


class ParseError(ValueError):
    """Exception raised by `load()` or `loads()` when given invalid input"""

    pass
