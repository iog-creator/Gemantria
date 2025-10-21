from __future__ import annotations

import sys
import trace
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set

import pytest


def _resolve_paths(root: Path, values: Sequence[str]) -> List[Path]:
    return [ (root / value).resolve() for value in values ]


@dataclass
class MiniCov:
    paths: List[Path]
    fail_under: float
    reports: Sequence[str]
    tracer: trace.Trace = field(init=False)
    overall: float = field(init=False, default=100.0)
    file_coverage: Dict[Path, float] = field(init=False, default_factory=dict)
    missing_lines: Dict[Path, Set[int]] = field(init=False, default_factory=dict)
    failed: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        ignoredirs = [str(Path(sys.prefix).resolve()), str(Path(sys.exec_prefix).resolve())]
        self.tracer = trace.Trace(count=True, trace=False, ignoredirs=ignoredirs)

    def start(self) -> None:
        sys.settrace(self.tracer.globaltrace)

    def stop(self) -> None:
        sys.settrace(None)

    def analyze(self) -> None:
        results = self.tracer.results()
        counts = getattr(results, "counts", {})
        executed: Dict[Path, Set[int]] = {}
        for (filename, lineno), _ in counts.items():
            path = Path(filename).resolve()
            if not self._is_included(path):
                continue
            executed.setdefault(path, set()).add(lineno)

        total_lines = 0
        total_hits = 0
        coverage_per_file: Dict[Path, float] = {}
        missing_by_file: Dict[Path, Set[int]] = {}
        for file_path in self._iter_python_files():
            relevant_lines = self._relevant_lines(file_path)
            if not relevant_lines:
                continue
            executed_lines = executed.get(file_path.resolve(), set())
            hits = len(relevant_lines & executed_lines)
            total_lines += len(relevant_lines)
            total_hits += hits
            coverage_per_file[file_path.resolve()] = (hits / len(relevant_lines)) * 100.0
            missing = relevant_lines - executed_lines
            if missing:
                missing_by_file[file_path.resolve()] = missing

        self.file_coverage = dict(sorted(coverage_per_file.items()))
        self.missing_lines = missing_by_file
        if total_lines:
            self.overall = (total_hits / total_lines) * 100.0
        else:
            self.overall = 100.0
        self.failed = self.overall < self.fail_under

    def _is_included(self, path: Path) -> bool:
        for target in self.paths:
            try:
                path.relative_to(target)
                return True
            except ValueError:
                if path == target:
                    return True
        return False

    def _iter_python_files(self) -> Iterable[Path]:
        for target in self.paths:
            if target.is_file() and target.suffix == ".py":
                if target.name != "__init__.py":
                    yield target
            elif target.is_dir():
                for candidate in sorted(target.rglob("*.py")):
                    if candidate.name == "__init__.py":
                        continue
                    yield candidate

    def _relevant_lines(self, path: Path) -> Set[int]:
        relevant: Set[int] = set()
        in_docstring = False
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "pragma: no cover" in line:
                continue
            if stripped in {"(", ")", "[", "]", "{", "}", "},", "],", "),"}:
                continue
            if in_docstring:
                if stripped.endswith("'''") or stripped.endswith('"""'):
                    in_docstring = False
                continue
            if stripped.startswith("'''") or stripped.startswith('"""'):
                if not (
                    stripped.endswith("'''")
                    or stripped.endswith('"""')
                    or stripped.count("'''") == 2
                    or stripped.count('"""') == 2
                ):
                    in_docstring = True
                continue
            relevant.add(index)
        return relevant


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("mini-cov")
    group.addoption(
        "--cov",
        action="append",
        dest="mini_cov_targets",
        default=[],
        metavar="PATH",
        help="Measure coverage for PATH (directory or file).",
    )
    group.addoption(
        "--cov-report",
        action="append",
        dest="mini_cov_reports",
        default=[],
        help="Supported for compatibility; only 'term-missing' is recognised.",
    )
    group.addoption(
        "--cov-fail-under",
        action="store",
        dest="mini_cov_fail_under",
        type=float,
        default=0.0,
        metavar="PERCENT",
        help="Fail if total coverage is less than PERCENT.",
    )


def pytest_configure(config: pytest.Config) -> None:
    targets = config.getoption("mini_cov_targets")
    if not targets:
        config._mini_cov = None  # type: ignore[attr-defined]
        return

    cov_paths = _resolve_paths(Path(config.rootpath), targets)
    fail_under = float(config.getoption("mini_cov_fail_under") or 0.0)
    reports = list(config.getoption("mini_cov_reports") or [])
    minicov = MiniCov(paths=cov_paths, fail_under=fail_under, reports=reports)
    config._mini_cov = minicov  # type: ignore[attr-defined]
    minicov.start()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    minicov: MiniCov | None = getattr(session.config, "_mini_cov", None)
    if minicov is None:
        return
    minicov.stop()
    minicov.analyze()
    if minicov.failed and exitstatus == 0:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_terminal_summary(terminalreporter: pytest.TerminalReporter, exitstatus: int) -> None:
    minicov: MiniCov | None = getattr(terminalreporter.config, "_mini_cov", None)
    if minicov is None:
        return

    if not minicov.file_coverage:
        terminalreporter.write_line("mini-cov: no files matched the requested --cov targets.")
    else:
        terminalreporter.write_line("mini-cov report:")
        for path, percentage in minicov.file_coverage.items():
            display_path = _display_path(Path(terminalreporter.config.rootpath), path)
            terminalreporter.write_line(f"  - {display_path}: {percentage:.1f}%")
        terminalreporter.write_line(
            "Overall coverage: "
            f"{minicov.overall:.1f}% (fail-under={minicov.fail_under:.1f}%)"
        )
        if "term-missing" in minicov.reports:
            for path, missing in minicov.missing_lines.items():
                display_path = _display_path(Path(terminalreporter.config.rootpath), path)
                missing_list = ", ".join(str(line) for line in sorted(missing))
                terminalreporter.write_line(f"    Missing lines in {display_path}: {missing_list}")
        if minicov.failed:
            terminalreporter.write_line("Coverage threshold not met.", yellow=True)


def _display_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
