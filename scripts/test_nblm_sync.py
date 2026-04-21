#!/usr/bin/env python3
"""Unit tests for nblm_sync.compute_diff.

Run with:
  /root/.openclaw/venvs/notebooklm/bin/python -m pytest \
      /root/.openclaw/workspace/scripts/test_nblm_sync.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from nblm_sync import (  # noqa: E402
    NoteRecord,
    NoteSnapshot,
    compute_diff,
)


def snap(note_id, notebook_id="nb1", title="t", content="c", notebook_title="NB1"):
    import hashlib

    return NoteSnapshot(
        note_id=note_id,
        notebook_id=notebook_id,
        notebook_title=notebook_title,
        title=title,
        content=content,
        content_hash=hashlib.sha256(content.encode()).hexdigest(),
    )


def rec(title="t", content_hash=None, notebook_title="NB1"):
    import hashlib

    return NoteRecord(
        title=title,
        content_hash=content_hash or hashlib.sha256(b"c").hexdigest(),
        notebook_title=notebook_title,
        last_seen="2026-04-20T02:00:00-03:00",
    )


def test_bootstrap_all_added():
    prev = {}
    curr = {"nb1": {"n1": snap("n1"), "n2": snap("n2", title="t2")}}
    diff = compute_diff(prev, curr)
    assert len(diff.added) == 2
    assert not diff.edited and not diff.removed and not diff.renamed


def test_no_change():
    prev = {"nb1": {"n1": rec()}}
    curr = {"nb1": {"n1": snap("n1")}}
    diff = compute_diff(prev, curr)
    assert diff.is_empty()


def test_added():
    prev = {"nb1": {"n1": rec()}}
    curr = {"nb1": {"n1": snap("n1"), "n2": snap("n2", title="t2")}}
    diff = compute_diff(prev, curr)
    assert [e.note_id for e in diff.added] == ["n2"]
    assert not diff.edited and not diff.removed


def test_edited():
    prev = {"nb1": {"n1": rec()}}
    curr = {"nb1": {"n1": snap("n1", content="c2")}}
    diff = compute_diff(prev, curr)
    assert [e.note_id for e in diff.edited] == ["n1"]


def test_removed():
    prev = {"nb1": {"n1": rec(), "n2": rec(title="t2")}}
    curr = {"nb1": {"n1": snap("n1")}}
    diff = compute_diff(prev, curr)
    assert [e.note_id for e in diff.removed] == ["n2"]


def test_renamed_same_content():
    prev = {"nb1": {"n1": rec(title="old")}}
    curr = {"nb1": {"n1": snap("n1", title="new")}}
    diff = compute_diff(prev, curr)
    assert len(diff.renamed) == 1
    e = diff.renamed[0]
    assert e.old_title == "old"
    assert e.title == "new"
    assert not diff.edited


def test_rename_plus_content_change_counts_as_edited():
    # If both title and content changed, it's classified as edited (not renamed).
    prev = {"nb1": {"n1": rec(title="old")}}
    curr = {"nb1": {"n1": snap("n1", title="new", content="changed")}}
    diff = compute_diff(prev, curr)
    assert [e.note_id for e in diff.edited] == ["n1"]
    assert not diff.renamed


def test_whole_notebook_removed():
    prev = {"nb1": {"n1": rec()}, "nb2": {"n5": rec(title="old")}}
    curr = {"nb1": {"n1": snap("n1")}}
    diff = compute_diff(prev, curr)
    assert [e.note_id for e in diff.removed] == ["n5"]


def test_mixed_across_notebooks():
    prev = {
        "nb1": {"n1": rec()},
        "nb2": {"n2": rec(title="t2")},
    }
    curr = {
        "nb1": {"n1": snap("n1", content="changed")},  # edited
        "nb2": {"n2": snap("n2", notebook_id="nb2", title="t2")},  # unchanged
        "nb3": {"n3": snap("n3", notebook_id="nb3")},  # new notebook, new note
    }
    diff = compute_diff(prev, curr)
    assert {e.note_id for e in diff.added} == {"n3"}
    assert {e.note_id for e in diff.edited} == {"n1"}
    assert not diff.removed and not diff.renamed


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
