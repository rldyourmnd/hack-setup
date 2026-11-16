"""Source validation must be independent of an installed account/toolchain."""
import importlib.util
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_checker(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def refuse_host_probe(*args, **kwargs):
    raise AssertionError("source validation attempted a host probe")


def test_codex_source_checks_do_not_inspect_installed_state(monkeypatch):
    checker = load_checker("codex_source_checker", "scripts/check_codex_setup.py")
    monkeypatch.setattr(checker, "codex_bin", refuse_host_probe)
    checker.check_config(source_only=True)
    checker.check_plugin_cache_sync(source_only=True)


def test_source_stack_still_checks_generated_consistency_without_probes(monkeypatch, tmp_path):
    checker = load_checker("stack_source_checker", "scripts/check_stack.py")
    monkeypatch.setenv("PATH", os.environ.get("PATH", ""))
    monkeypatch.setattr(checker, "run_probe", refuse_host_probe)
    assert checker.main(["--source"]) == 0
    stale = tmp_path / "stack-standard.md"
    stale.write_text("stale generated output")
    monkeypatch.setattr(checker, "STANDARD_PATH", stale)
    with pytest.raises(checker.CheckError, match="stale"):
        checker.main(["--source"])


def test_syntax_check_writes_no_bytecode_and_keeps_compile_errors(tmp_path):
    checker = load_checker("syntax_source_checker", "scripts/check_codex_setup.py")
    source = tmp_path / "subject.py"
    source.write_text("answer = 42\n")
    checker.py_compile(str(source))
    assert list(tmp_path.iterdir()) == [source]
    source.write_text("return 42\n")
    with pytest.raises(checker.CheckError, match="must compile"):
        checker.py_compile(str(source))
    assert list(tmp_path.iterdir()) == [source]


def test_devin_source_reserves_hook_execution_for_native_checks(monkeypatch):
    checker = load_checker("devin_source_checker", "devin-setup/scripts/check_devin_setup.py")
    monkeypatch.setattr(checker, "check_devin_mode_smoke", refuse_host_probe)
    assert checker.main(source_only=True) == 0


def test_source_stack_refuses_a_writing_mode():
    checker = load_checker("stack_source_write_guard", "scripts/check_stack.py")
    original = checker.STANDARD_PATH.read_bytes()
    with pytest.raises(SystemExit):
        checker.main(["--source", "--write"])
    assert checker.STANDARD_PATH.read_bytes() == original


def test_devin_hook_syntax_validation_does_not_use_a_bytecode_writer(monkeypatch):
    import py_compile

    checker = load_checker("devin_source_bytecode_guard", "devin-setup/scripts/check_devin_setup.py")
    monkeypatch.setattr(py_compile, "compile", refuse_host_probe)
    checker.check_hooks()
    assert checker.ERRORS == []
