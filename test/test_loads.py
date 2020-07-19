import pytest
from   entry_points_txt import EntryPoint, ParseError, loads

@pytest.mark.parametrize('txt,eps', [
    ('', {}),

    (
        '[console_scripts]\n'
        'foo = bar\n',
        {
            "console_scripts": {
                "foo": EntryPoint('console_scripts', 'foo', 'bar', None, ())
            },
        },
    ),

    (
        '[console_scripts]\n'
        'foo = bar:baz\n',
        {
            "console_scripts": {
                "foo": EntryPoint('console_scripts', 'foo', 'bar', 'baz', ())
            },
        },
    ),

    (
        '[console_scripts]\n'
        'foo = bar.apple:baz.banana\n',
        {
            "console_scripts": {
                "foo": EntryPoint(
                    'console_scripts',
                    'foo',
                    'bar.apple',
                    'baz.banana',
                    (),
                )
            },
        },
    ),

    (
        '[console_scripts]\n'
        'foo = bar:baz[quux]\n',
        {
            "console_scripts": {
                "foo": EntryPoint(
                    'console_scripts',
                    'foo',
                    'bar',
                    'baz',
                    ('quux',),
                )
            },
        },
    ),

    (
        '[console_scripts]\n'
        'foo = bar:baz[quux,glarch]\n',
        {
            "console_scripts": {
                "foo": EntryPoint('console_scripts', 'foo', 'bar', 'baz', ('quux', 'glarch'))
            },
        },
    ),

    (
        '[console_scripts]\n'
        'foo = bar : baz [ quux , glarch ] \n',
        {
            "console_scripts": {
                "foo": EntryPoint('console_scripts', 'foo', 'bar', 'baz', ('quux', 'glarch'))
            },
        },
    ),

    (
        '[console_scripts]\n'
        'foo = bar:baz\n',
        'apple = red:delicious\n'
        '[glarch.quux]\n'
        'thing-of-things = one.two\n',
        {
            "console_scripts": {
                "foo": EntryPoint('console_scripts', 'foo', 'bar', 'baz', ())
                "apple": EntryPoint(
                    'console_scripts',
                    'apple',
                    'red',
                    'delicious',
                    (),
                ),
            },
            "glarch.quux": {
                "thing-of-things": EntryPoint(
                    'glarch.quux',
                    'thing-of-things',
                    'one.two',
                    None,
                    (),
                ),
            },
        },
    ),

    (
        '[console_scripts]\n'
        'foo = bar:baz\n',
        ';apple = red:delicious\n'
        '[glarch.quux]\n'
        '#thing-of-things = one.two\n',
        {
            "console_scripts": {
                "foo": EntryPoint('console_scripts', 'foo', 'bar', 'baz', ())

            },
        },
    ),

])
def test_loads(txt, eps):
    assert loads(txt) == eps

@pytest.mark.parametrize('txt,errmsg', [
    (
        '[console_scripts]\n'
        'foo = bar:\n',
        'Missing object name after colon'
    ),
])
def test_loads_error(txt, errmsg):
    with pytest.raises(ParseError) as excinfo:
        loads(txt)
    assert str(excinfo.value) == errmsg
