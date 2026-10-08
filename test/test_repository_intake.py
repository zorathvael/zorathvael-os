from __future__ import annotations

from scripts.ingest_repository_request import normalize_repository_url, parse_issue_url, request_key


def test_normalize_repository_url() -> None:
    url, repo = normalize_repository_url("https://github.com/Zorathvael/zorathvael-os.git")
    assert url == "https://github.com/Zorathvael/zorathvael-os"
    assert repo == "Zorathvael/zorathvael-os"


def test_parse_issue_url_requires_same_repository() -> None:
    parsed = parse_issue_url(
        "https://github.com/zorathvael/zorathvael-os/issues/42",
        "zorathvael/zorathvael-os",
    )
    assert parsed == ("https://github.com/zorathvael/zorathvael-os/issues/42", 42)


def test_parse_issue_url_rejects_other_repository() -> None:
    try:
        parse_issue_url(
            "https://github.com/other/project/issues/42",
            "zorathvael/zorathvael-os",
        )
    except ValueError as exc:
        assert "target repository" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_request_key_is_deterministic() -> None:
    assert request_key("a/b", "https://github.com/a/b/issues/1", "problem") == request_key(
        "A/B", "HTTPS://GITHUB.COM/A/B/ISSUES/1", "problem"
    )
