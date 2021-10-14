import configparser
import email.message
from typing import Any
import pytest
from entry_points_txt import EntryPoint


@pytest.mark.parametrize(
    "ep,obj",
    [
        (
            EntryPoint("group", "foo", "configparser", None, ()),
            configparser,
        ),
        (
            EntryPoint("group", "foo", "configparser", "ConfigParser", ()),
            configparser.ConfigParser,
        ),
        (
            EntryPoint(
                "group", "foo", "configparser", "ConfigParser.BOOLEAN_STATES", ()
            ),
            configparser.ConfigParser.BOOLEAN_STATES,
        ),
        (
            EntryPoint("group", "foo", "email.message", None, ()),
            email.message,
        ),
        (
            EntryPoint("group", "foo", "email.message", "EmailMessage", ()),
            email.message.EmailMessage,
        ),
    ],
)
def test_ep_load(ep: EntryPoint, obj: Any) -> None:
    assert ep.load() is obj
