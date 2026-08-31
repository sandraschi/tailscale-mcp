"""Unit tests for ACL policy health analysis (missing-ip-grant pitfall, BUG-022)."""

from tailscalemcp.operations.network import analyze_acl_policy

BROKEN_APP_ONLY = (
    '{"grants": [{"src": ["autogroup:member"], "dst": ["autogroup:member"],'
    ' "app": {"tailscale.com/cap/drive": [{"shares": ["*"], "access": "rw"}]}}]}'
)

FIXED = (
    '{"grants": ['
    '{"src": ["autogroup:member"], "dst": ["autogroup:member"], "ip": ["*"]},'
    '{"src": ["autogroup:member"], "dst": ["autogroup:member"],'
    ' "app": {"tailscale.com/cap/drive": [{"shares": ["*"], "access": "rw"}]}}'
    "]}"
)

COMMENTED_TEMPLATE = (
    "// Example/default ACLs for unrestricted connections.\n"
    "{\n"
    '\t"grants": [\n'
    '\t\t//{"src": ["*"], "dst": ["*"], "ip": ["*"]},\n'
    "\t],\n"
    "}"
)

TRAILING_COMMA = (
    '{"grants": [{"src": ["autogroup:member"], "dst": ["autogroup:member"],'
    ' "ip": ["*"],},],}'
)


def test_app_only_grant_is_unhealthy():
    result = analyze_acl_policy({"acl": BROKEN_APP_ONLY})
    assert result["healthy"] is False
    assert result["ip_grants"] == 0
    assert result["app_only_grants"] == 1
    assert result["grants_count"] == 1
    assert result["suggestion"]
    assert any("ip field" in f for f in result["findings"])


def test_ip_grant_is_healthy():
    result = analyze_acl_policy({"acl": FIXED})
    assert result["healthy"] is True
    assert result["ip_grants"] == 1
    assert result["app_only_grants"] == 1
    assert result["suggestion"] is None
    assert any("App-only" in f for f in result["findings"])


def test_commented_template_is_unhealthy():
    result = analyze_acl_policy({"acl": COMMENTED_TEMPLATE})
    assert result["healthy"] is False
    assert result["ip_grants"] == 0


def test_unparseable_acl_reports_unhealthy():
    result = analyze_acl_policy({"acl": "{not json"})
    assert result["healthy"] is False
    assert any("parse" in f for f in result["findings"])
    assert result["suggestion"]


def test_parsed_policy_dict_accepted():
    result = analyze_acl_policy({"grants": [{"src": ["*"], "dst": ["*"], "ip": ["*"]}]})
    assert result["healthy"] is True
    assert result["ip_grants"] == 1


def test_trailing_commas_are_tolerated():
    result = analyze_acl_policy({"acl": TRAILING_COMMA})
    assert result["healthy"] is True
    assert result["ip_grants"] == 1
