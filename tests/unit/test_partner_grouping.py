"""Tests for partner tailnets device grouping."""

from tailscalemcp.tools.partner_tailnets_tool import _group_devices_by_login


def test_group_devices_by_login_empty() -> None:
    assert _group_devices_by_login([]) == {}


def test_group_devices_by_login_unknown() -> None:
    out = _group_devices_by_login([{"id": "n1", "name": "a"}])
    assert "(unknown)" in out
    assert len(out["(unknown)"]) == 1


def test_group_devices_by_login_buckets() -> None:
    devs = [
        {"id": "1", "user": "alice@github", "name": "m1"},
        {"id": "2", "user": "alice@github", "name": "m2"},
        {"id": "3", "user": "bob@github", "name": "m3"},
    ]
    out = _group_devices_by_login(devs)
    assert len(out["alice@github"]) == 2
    assert len(out["bob@github"]) == 1
