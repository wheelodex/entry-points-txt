import pytest
from   entry_points_txt import EntryPoint, dumps

@pytest.mark.parametrize('eps,txt', [
    ({}, ''),
    ({"console_scripts": {}}, ''),

    (
        {
            "console_scripts": {
                "foo": EntryPoint("console_scripts", "foo", "bar", None, ()),
            }
        },
        '[console_scripts]\n'
        'foo = bar\n'
    ),

    (
        {
            "console_scripts": {
                "foo": EntryPoint("console_scripts", "foo", "bar", None, ()),
                "apple": EntryPoint(
                    "console_scripts",
                    "apple",
                    "banana",
                    "coconut",
                    (),
                ),
            }
        },
        '[console_scripts]\n'
        'foo = bar\n'
        'apple = banana:coconut\n'
    ),

    (
        {
            "console_scripts": {
                "foo": EntryPoint("console_scripts", "foo", "bar", None, ()),
                "apple": EntryPoint(
                    "console_scripts",
                    "apple",
                    "banana",
                    "coconut",
                    (),
                ),
            },
            "some.group": {
                "thingy": EntryPoint(
                    "some.group",
                    "thingy",
                    "module",
                    "object",
                    ("xtra",),
                ),
            }
        },
        '[console_scripts]\n'
        'foo = bar\n'
        'apple = banana:coconut\n'
        '\n'
        '[some.group]\n'
        'thingy = module:object [xtra]\n'
    ),
])
def test_dumps(eps, txt):
    assert dumps(eps) == txt

def test_dumps_group_mismatch():
    with pytest.raises(ValueError) as excinfo:
        dumps({
            "group1": {
                "foo": EntryPoint('group2', 'foo', 'module', None, ())
            }
        })
    assert str(excinfo.value) == (
        "Group mismatch: entry point with group 'group2' placed under 'group1'"
        " dict"
    )

def test_dumps_name_mismatch():
    with pytest.raises(ValueError) as excinfo:
        dumps({
            "group1": {
                "foo": EntryPoint('group1', 'bar', 'module', None, ())
            }
        })
    assert str(excinfo.value) == (
        "Name mismatch: entry point with name 'bar' placed under key 'foo'"
    )
