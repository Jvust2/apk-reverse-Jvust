"""Regression tests for the documented-command gate itself.

`check_commands.py` is the gate that proves other documentation is runnable, so a blind spot in it
is worth more than a blind spot elsewhere: it turns "146 commands checked, 0 drift" into a claim the
repository cannot back. One such blind spot is pinned here, exactly as it was found.

**What was wrong.** `resolve_script()` tried the *document's own directory* first when resolving a
relative path. A bare `python analyze_pair.py` written inside `docs/tool-verification/` therefore
resolved to `tools/_work/bench/unpack/b3/analyze_pair.py` -- a real file, inside the gitignored
workbench -- and scored `ok`. Seven commands in two evidence files used that form while the same
files wrote the correct path elsewhere, and a reader copying one from the repository root gets
"No such file". The gate said the documentation was clean.

The tests below drive the resolver and the finding classifier directly rather than through the CLI,
so they stay fast and do not depend on the current state of the documentation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from conftest import REPO_ROOT

pytestmark = pytest.mark.integration

CHECK_COMMANDS = REPO_ROOT / "check_commands.py"


@pytest.fixture(scope="module")
def gate():
    """The gate as a module, so its internals can be driven without a subprocess."""
    sys.path.insert(0, str(REPO_ROOT))
    import importlib

    return importlib.import_module("check_commands")


def _workbench_script_name(gate):
    """A `.py` basename that exists only under tools/, or skip if the workbench is absent."""
    names = sorted(gate._workbench_names())
    if not names:
        pytest.skip("no workbench present (tools/ is gitignored and may not exist in a checkout)")
    shipped = {p.name for p in (REPO_ROOT / "skills" / "apk-reverse" / "scripts").glob("*.py")}
    root = {p.name for p in REPO_ROOT.glob("*.py")}
    for name in names:
        if name not in shipped and name not in root:
            return name
    pytest.skip("every workbench script name is also shipped; nothing to test with")


def test_a_bare_name_that_only_exists_in_the_workbench_is_drift(gate):
    """The exact defect: the name exists *somewhere*, which used to be enough to pass it."""
    name = _workbench_script_name(gate)
    doc = str(REPO_ROOT / "docs" / "tool-verification" / "EXTENSION-extraction-shell-bench.md")
    path, why = gate.resolve_script(name, doc, include_workbench=False)
    assert path is None
    assert why == "unqualified-workbench", why

    text = "```\n$ python %s --flag\n```\n" % name
    findings = gate.command_findings(doc, text, {}, False)
    kinds = [f["kind"] for f in findings]
    assert "unqualified-workbench" in kinds, findings


def test_a_path_qualified_workbench_reference_is_a_skip_not_drift(gate):
    """`tools/_work/...` is deliberate in an evidence record: a skip, reported with its reason."""
    name = _workbench_script_name(gate)
    doc = str(REPO_ROOT / "docs" / "tool-verification" / "EXTENSION-extraction-shell-bench.md")
    _path, why = gate.resolve_script("tools/_work/somewhere/%s" % name, doc, include_workbench=False)
    assert why == "workbench"


def test_a_bare_name_after_a_cd_in_the_same_block_is_not_drift(gate):
    """A block that says `cd tools/_work/bench/repos/dcc` tells the reader where to stand."""
    name = _workbench_script_name(gate)
    doc = str(REPO_ROOT / "docs" / "tool-verification" / "EXTENSION-java2c.md")
    text = "```\n$ cd tools/_work/bench/repos/dcc\n$ python %s --no-build\n```\n" % name
    findings = gate.command_findings(doc, text, {}, False)
    kinds = [f["kind"] for f in findings]
    assert "unqualified-workbench" not in kinds, findings
    assert "workbench-after-cd" in kinds, findings


def test_the_external_dcc_entry_point_is_never_drift(gate):
    """`python dcc.py` after `cd tools/_work/bench/repos/dcc` runs inside the external dcc
    checkout, so it is a skip on every machine -- including one without the workbench.

    The name is declared in EXTERNAL_SCRIPTS because the workbench-name recognition that
    used to cover it needs tools/ to exist: on a clean checkout `dcc.py` degraded from
    workbench-after-cd to missing-script drift, and the gate failed away from the machine
    that wrote the record.
    """
    doc = str(REPO_ROOT / "docs" / "tool-verification" / "EXTENSION-java2c.md")
    _path, why = gate.resolve_script("dcc.py", doc, include_workbench=False, chdir=True)
    if gate._workbench_names():
        assert why == "workbench-after-cd", why
    else:
        assert why == "external", why

    text = "```\n$ cd tools/_work/bench/repos/dcc\n$ python dcc.py --no-build\n```\n"
    findings = gate.command_findings(doc, text, {}, False)
    kinds = [f["kind"] for f in findings]
    assert "missing-script" not in kinds, findings
    assert "unqualified-workbench" not in kinds, findings
    assert any(k in ("workbench-after-cd", "external") for k in kinds), findings


def test_a_shipped_script_resolves_from_the_repository_root(gate):
    """The order that matters: root, then the skill's scripts, then the document's own directory."""
    doc = str(REPO_ROOT / "docs" / "tool-verification" / "README.md")
    path, why = gate.resolve_script("check_repo.py", doc, include_workbench=False)
    assert why == "ok" and path and path.endswith("check_repo.py")
    path, why = gate.resolve_script("skills/apk-reverse/scripts/scan_leaks.py", doc,
                                    include_workbench=False)
    assert why == "ok" and path and path.endswith("scan_leaks.py")


def test_the_committed_tree_reports_no_drift(gate, tmp_path):
    """The gate's own verdict on this repository, run in-process so it cannot drift silently."""
    docs = gate.collect_docs(None)
    findings = []
    cache = {}
    for doc in docs:
        try:
            text = Path(doc).read_text(encoding="utf-8")
        except OSError:
            continue
        findings.extend(gate.command_findings(doc, text, cache, False))
    drift = [f for f in findings
             if f["kind"] in ("unknown-flag", "missing-script", "unqualified-workbench")]
    detail = "\n".join("  %s:%s %s (%s)" % (f["doc"], f["line"], f["command"], f["kind"])
                       for f in drift[:20])
    assert not drift, "documented commands that cannot run:\n%s" % detail
