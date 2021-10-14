import pytest
from entry_points_txt import EntryPoint, EntryPointSet, ParseError, loads


@pytest.mark.parametrize(
    "txt,eps",
    [
        ("", {}),
        (
            "[console_scripts]\n" "foo = bar\n",
            {
                "console_scripts": {
                    "foo": EntryPoint("console_scripts", "foo", "bar", None, ())
                },
            },
        ),
        (
            "[console_scripts]\n" "foo = bar:baz\n",
            {
                "console_scripts": {
                    "foo": EntryPoint("console_scripts", "foo", "bar", "baz", ())
                },
            },
        ),
        (
            "[console_scripts]\n" "foo = bar.apple:baz.banana\n",
            {
                "console_scripts": {
                    "foo": EntryPoint(
                        "console_scripts",
                        "foo",
                        "bar.apple",
                        "baz.banana",
                        (),
                    )
                },
            },
        ),
        (
            "[console_scripts]\n" "foo = bar:baz[]\n",
            {
                "console_scripts": {
                    "foo": EntryPoint("console_scripts", "foo", "bar", "baz", ()),
                },
            },
        ),
        (
            "[console_scripts]\n" "foo = bar:baz[  ]\n",
            {
                "console_scripts": {
                    "foo": EntryPoint("console_scripts", "foo", "bar", "baz", ()),
                },
            },
        ),
        (
            "[console_scripts]\n" "foo = bar[quux]\n",
            {
                "console_scripts": {
                    "foo": EntryPoint(
                        "console_scripts",
                        "foo",
                        "bar",
                        None,
                        ("quux",),
                    )
                },
            },
        ),
        (
            "[console_scripts]\n" "foo = bar:baz[quux]\n",
            {
                "console_scripts": {
                    "foo": EntryPoint(
                        "console_scripts",
                        "foo",
                        "bar",
                        "baz",
                        ("quux",),
                    )
                },
            },
        ),
        (
            "[console_scripts]\n" "foo = bar:baz[quux,glarch]\n",
            {
                "console_scripts": {
                    "foo": EntryPoint(
                        "console_scripts",
                        "foo",
                        "bar",
                        "baz",
                        ("quux", "glarch"),
                    )
                },
            },
        ),
        (
            " [ console_scripts ] \n" " foo = bar : baz [ quux , glarch ] \n",
            {
                "console_scripts": {
                    "foo": EntryPoint(
                        "console_scripts",
                        "foo",
                        "bar",
                        "baz",
                        ("quux", "glarch"),
                    )
                },
            },
        ),
        (
            "[console_scripts]\n"
            "foo = bar:baz\n"
            "apple = red:delicious\n"
            "[glarch.quux]\n"
            "thing-of-things = one.two\n",
            {
                "console_scripts": {
                    "foo": EntryPoint("console_scripts", "foo", "bar", "baz", ()),
                    "apple": EntryPoint(
                        "console_scripts",
                        "apple",
                        "red",
                        "delicious",
                        (),
                    ),
                },
                "glarch.quux": {
                    "thing-of-things": EntryPoint(
                        "glarch.quux",
                        "thing-of-things",
                        "one.two",
                        None,
                        (),
                    ),
                },
            },
        ),
        (
            "[console_scripts]\n"
            "foo = bar:baz\n"
            ";apple = red:delicious\n"
            "[glarch.quux]\n"
            "#thing-of-things = one.two\n",
            {
                "console_scripts": {
                    "foo": EntryPoint("console_scripts", "foo", "bar", "baz", ())
                },
            },
        ),
        (
            "[glarch.quux]\n" "thing of things = one.two\n",
            {
                "glarch.quux": {
                    "thing of things": EntryPoint(
                        "glarch.quux",
                        "thing of things",
                        "one.two",
                        None,
                        (),
                    ),
                },
            },
        ),
        (
            "[console_scripts]\n"
            "foo = bar:baz\n"
            "\n"
            "[console_scripts]\n"
            "apple = red:delicious\n",
            {
                "console_scripts": {
                    "foo": EntryPoint("console_scripts", "foo", "bar", "baz", ()),
                    "apple": EntryPoint(
                        "console_scripts",
                        "apple",
                        "red",
                        "delicious",
                        (),
                    ),
                },
            },
        ),
        (
            "[console_scripts]\n" "foo = bar:baz\n" "foo = quux\n",
            {
                "console_scripts": {
                    "foo": EntryPoint("console_scripts", "foo", "quux", None, ()),
                },
            },
        ),
        (
            "[console_scripts]\n" "foo = bar:baz\n" "[thingy]\n" "foo = quux\n",
            {
                "console_scripts": {
                    "foo": EntryPoint("console_scripts", "foo", "bar", "baz", ()),
                },
                "thingy": {
                    "foo": EntryPoint("thingy", "foo", "quux", None, ()),
                },
            },
        ),
    ],
)
def test_loads(txt: str, eps: EntryPointSet) -> None:
    assert loads(txt) == eps


@pytest.mark.parametrize(
    "txt,errmsg",
    [
        (
            "foo = bar:baz\n" "[console_scripts]\n",
            "Entry point line occurs before any group headers",
        ),
        (
            "[console_scripts\n" "]\n" "foo = bar\n",
            "Group header missing closing bracket",
        ),
        ("[]\n" "foo = bar\n", "Empty group name"),
        ("[  ]\n" "foo = bar\n", "Empty group name"),
        ("[group-name]\n" "foo = bar\n", "Invalid group name: 'group-name'"),
        ("[group name]\n" "foo = bar\n", "Invalid group name: 'group name'"),
        ("[group.]\n" "foo = bar\n", "Invalid group name: 'group.'"),
        ("[group.*]\n" "foo = bar\n", "Invalid group name: 'group.*'"),
        ("[console_scripts]\n" "foo bar\n", "Invalid line (no '='): 'foo bar'"),
        ("[console_scripts]\n" " = bar\n", "Empty entry point name"),
        ("[console_scripts]\n" "foo = \n", "Empty module name"),
        ("[console_scripts]\n" "foo = :bar\n", "Empty module name"),
        ("[console_scripts]\n" "foo = [xtra]\n", "Empty module name"),
        (
            "[console_scripts]\n" "foo = a-module:bar\n",
            "Invalid module name: 'a-module'",
        ),
        ("[console_scripts]\n" "foo = bar.def:baz\n", "Invalid module name: 'bar.def'"),
        ("[console_scripts]\n" "foo = bar = baz\n", "Invalid module name: 'bar = baz'"),
        ("[console_scripts]\n" "foo = bar:\n", "Missing attribute name after colon"),
        (
            "[console_scripts]\n" "foo = bar: [xtra]\n",
            "Missing attribute name after colon",
        ),
        (
            "[console_scripts]\n" "foo = bar:an object\n",
            "Invalid attribute name: 'an object'",
        ),
        (
            "[console_scripts]\n" "foo = bar:obj.def\n",
            "Invalid attribute name: 'obj.def'",
        ),
        (
            "[console_scripts]\n" "foo = bar:baz:quux\n",
            "Invalid attribute name: 'baz:quux'",
        ),
        (
            "[console_scripts]\n" "foo = bar:baz[xtra\n" "]\n",
            "Extras missing closing bracket",
        ),
        (
            "[console_scripts]\n" "foo = bar:baz[xtra]glarch\n",
            "Trailing characters after extras",
        ),
        ("[console_scripts]\n" "foo = bar:baz[foo.]\n", "Invalid extra: 'foo.'"),
        ("[console_scripts]\n" "foo = bar:baz[foo,]\n", "Invalid extra: ''"),
    ],
)
def test_loads_error(txt: str, errmsg: str) -> None:
    with pytest.raises(ParseError) as excinfo:
        loads(txt)
    assert str(excinfo.value) == errmsg
