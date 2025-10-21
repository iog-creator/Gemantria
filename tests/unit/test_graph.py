import pytest

from src.graph import GraphRunResult, HelloGraph, main


def test_graph_run_result_message() -> None:
    result = GraphRunResult(book="Genesis", mode="START", dry_run=True)
    assert "[dry-run]" in result.message()
    assert str(result) == result.message()


def test_hello_graph_requires_book() -> None:
    with pytest.raises(ValueError):
        HelloGraph("")


def test_hello_graph_run_requires_dry_run() -> None:
    graph = HelloGraph("Genesis")

    with pytest.raises(RuntimeError):
        graph.run(mode="start", dry_run=False)

    result = graph.run(mode="continue", dry_run=True)
    assert result.mode == "CONTINUE"


def test_cli_entrypoint(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["Genesis", "--mode", "start", "--dry-run"])
    assert exit_code == 0
    captured = capsys.readouterr().out
    assert "Would execute START for Genesis" in captured
