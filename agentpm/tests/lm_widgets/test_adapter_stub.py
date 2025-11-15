def test_adapter_stub_compiles():
    from agentpm.lm_widgets.adapter import load_lm_indicator_widget_props

    assert callable(load_lm_indicator_widget_props)
