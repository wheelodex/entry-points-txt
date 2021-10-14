import pytest
from entry_points_txt import EntryPoint


@pytest.mark.parametrize(
    "ep,line",
    [
        (
            EntryPoint("group", "foo", "bar", None, ()),
            "foo = bar",
        ),
        (
            EntryPoint("group", "foo", "bar", "baz", ()),
            "foo = bar:baz",
        ),
        (
            EntryPoint("group", "foo", "bar", None, ("xtra",)),
            "foo = bar [xtra]",
        ),
        (
            EntryPoint("group", "foo", "bar", "baz", ("xtra",)),
            "foo = bar:baz [xtra]",
        ),
        (
            EntryPoint("group", "foo", "bar", None, ("xtra", "ytra")),
            "foo = bar [xtra,ytra]",
        ),
        (
            EntryPoint("group", "foo", "bar", "baz", ("xtra", "ytra")),
            "foo = bar:baz [xtra,ytra]",
        ),
    ],
)
def test_to_line(ep: EntryPoint, line: str) -> None:
    assert ep.to_line() == line
