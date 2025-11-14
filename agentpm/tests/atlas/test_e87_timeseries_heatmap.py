import os, pytest

EXPORT = "share/atlas/control_plane/compliance_timeseries.json"
HTML_TS = "docs/atlas/dashboard/compliance_timeseries.html"
HTML_HM = "docs/atlas/dashboard/compliance_heatmap.html"


@pytest.mark.xfail(reason="E87 not implemented yet")
def test_e87_export_present():
    assert os.path.exists(EXPORT)


@pytest.mark.xfail(reason="E87 not implemented yet")
def test_e87_html_timeseries_present():
    assert os.path.exists(HTML_TS)


@pytest.mark.xfail(reason="E87 not implemented yet")
def test_e87_html_heatmap_present():
    assert os.path.exists(HTML_HM)


@pytest.mark.xfail(reason="E87 not implemented yet")
def test_e87_guard_runs_and_reports():
    from subprocess import run

    proc = run(
        ["python3", "scripts/guards/guard_compliance_timeseries_backlinks.py"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode in (0, 1)
    assert proc.stdout.strip() != ""
