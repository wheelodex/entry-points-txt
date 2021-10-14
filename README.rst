.. image:: http://www.repostatus.org/badges/latest/active.svg
    :target: http://www.repostatus.org/#active
    :alt: Project Status: Active — The project has reached a stable, usable
          state and is being actively developed.

.. image:: https://github.com/jwodder/entry-points-txt/workflows/Test/badge.svg?branch=master
    :target: https://github.com/jwodder/entry-points-txt/actions?workflow=Test
    :alt: CI Status

.. image:: https://codecov.io/gh/jwodder/entry-points-txt/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/entry-points-txt

.. image:: https://img.shields.io/pypi/pyversions/entry-points-txt.svg
    :target: https://pypi.org/project/entry-points-txt/

.. image:: https://img.shields.io/github/license/jwodder/entry-points-txt.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/entry-points-txt>`_
| `PyPI <https://pypi.org/project/entry-points-txt/>`_
| `Issues <https://github.com/jwodder/entry-points-txt/issues>`_
| `Changelog <https://github.com/jwodder/entry-points-txt/blob/master/CHANGELOG.md>`_

``entry-points-txt`` provides functions for reading & writing
``entry_points.txt`` files according to `the spec`_.  That is the one thing it
does, and it endeavors to do it well.

.. _the spec: https://packaging.python.org/specifications/entry-points/

Installation
============
``entry-points-txt`` requires Python 3.6 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install
``entry-points-txt``::

    python3 -m pip install entry-points-txt


API
===

``EntryPoint``
--------------

.. code:: python

    class EntryPoint(NamedTuple)

A representation of an entry point as a namedtuple.  Instances have the
following attributes and methods:

``group: str``
   The name of the entry point group (e.g., ``"console_scripts"``)

``name: str``
   The name of the entry point

``module: str``
   The module portion of the attribute reference (the part before the colon)

``attr: Optional[str]``
   The attribute/object portion of the attribute reference (the part after the
   colon), or ``None`` if not specified

``extras: Tuple[str, ...]``
   Extras required for the entry point

``load() -> Any``
   Returns the object referred to by the entry point

``to_line() -> str``
   Returns the representation of the entry point as a line in
   ``entry_points.txt``, i.e., a line of the form ``name = module:attr
   [extras]``

``EntryPointSet``
-----------------

.. code:: python

    EntryPointSet = Dict[str, Dict[str, EntryPoint]]

An alias for the return type of ``load()`` & ``loads()`` and the argument type
of ``dump()`` & ``dumps()``.  Entry points are organized into a ``dict`` that
maps group names to sub-``dict``\s that map entry point names to ``EntryPoint``
instances.

``load()``
----------

.. code:: python

    entry_points_txt.load(fp: IO[str]) -> EntryPointSet

Parse a file-like object as an ``entry_points.txt``-format file and return the
results.

For example, the following input:

.. code:: ini

    [console_scripts]
    foo = package.__main__:main
    bar = package.cli:klass.attr

    [thingy.extension]
    quux = package.thingy [xtr]

would be parsed as:

.. code:: python

    {
        "console_scripts": {
            "foo": EntryPoint(group="console_scripts", name="foo", module="package.__main__", attr="main", extras=()),
            "bar": EntryPoint(group="console_scripts", name="bar", module="package.cli", attr="klass.attr", extras=()),
        },
        "thingy.extension": {
            "quux": EntryPoint(group="thingy.extension", name="quux", module="package.thingy", attr=None, extras=("xtr",)),
        },
    }

``loads()``
-----------

.. code:: python

    entry_points_txt.loads(s: str) -> EntryPointSet

Like ``load()``, but reads from a string instead of a filehandle

``dump()``
----------

.. code:: python

    entry_points_txt.dump(eps: EntryPointSet, fp: IO[str]) -> None

Write a collection of entry points to a file-like object in
``entry_points.txt`` format.  A ``ValueError`` is raised and nothing is written
if the group or name key under which an ``EntryPoint`` is located does not
match its ``group`` or ``name`` attribute.

``dumps()``
-----------

.. code:: python

    entry_points_txt.dumps(eps: EntryPointSet) -> str

Like ``dump()``, but returns a string instead of writing to a filehandle

``dump_list()``
---------------

.. code:: python

    entry_points_txt.dump_list(eps: Iterable[EntryPoint], fp: IO[str]) -> None

Write an iterable of entry points to a file-like object in ``entry_points.txt``
format.  If two or more entry points have the same group & name, only the last
one will be output.

``dumps_list()``
----------------

.. code:: python

    entry_points_txt.dumps_list(eps: Iterable[EntryPoint]) -> str

Like ``dump_list()``, but returns a string instead of writing to a filehandle

``ParseError``
--------------

.. code:: python

    class ParseError(ValueError)

Exception raised by ``load()`` or ``loads()`` when given invalid input
