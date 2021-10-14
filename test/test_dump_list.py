from io import StringIO
from typing import List
import pytest
from entry_points_txt import EntryPoint, dump_list, dumps_list

TEST_CASES = [
    ([], ""),
    (
        [EntryPoint("console_scripts", "foo", "bar", "baz", ())],
        "[console_scripts]\n" "foo = bar:baz\n",
    ),
    (
        [
            EntryPoint("console_scripts", "foo", "bar", "baz", ()),
            EntryPoint("console_scripts", "apple", "banana", "coconut", ()),
        ],
        "[console_scripts]\n" "foo = bar:baz\n" "apple = banana:coconut\n",
    ),
    (
        [
            EntryPoint("glarch", "name", "module", None, ()),
            EntryPoint("console_scripts", "foo", "bar", "baz", ()),
            EntryPoint("console_scripts", "apple", "banana", "coconut", ()),
        ],
        "[glarch]\n"
        "name = module\n"
        "\n"
        "[console_scripts]\n"
        "foo = bar:baz\n"
        "apple = banana:coconut\n",
    ),
    (
        [
            EntryPoint("console_scripts", "foo", "bar", "baz", ()),
            EntryPoint("console_scripts", "foo", "quux", None, ()),
        ],
        "[console_scripts]\n" "foo = quux\n",
    ),
    (
        [
            EntryPoint("console_scripts", "foo", "bar", "baz", ()),
            EntryPoint("thingy", "foo", "quux", None, ()),
        ],
        "[console_scripts]\n" "foo = bar:baz\n" "\n" "[thingy]\n" "foo = quux\n",
    ),
]


@pytest.mark.parametrize("eps,txt", TEST_CASES)
def test_dump_list(eps: List[EntryPoint], txt: str) -> None:
    fp = StringIO()
    dump_list(eps, fp)
    assert fp.getvalue() == txt


@pytest.mark.parametrize("eps,txt", TEST_CASES)
def test_dumps_list(eps: List[EntryPoint], txt: str) -> None:
    assert dumps_list(eps) == txt
