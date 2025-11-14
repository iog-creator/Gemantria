import pytest, os


@pytest.mark.xfail(reason="E86 not implemented yet")
def test_e86_export_present():
    assert os.path.exists("share/atlas/control_plane/e86_compliance_summary.json")


@pytest.mark.xfail(reason="E86 not implemented yet")
def test_e86_dashboard_present():
    assert os.path.exists("docs/atlas/compliance/e86_compliance_summary.html")
