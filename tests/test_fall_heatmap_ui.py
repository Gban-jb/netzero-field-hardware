"""Regression: the five-tab Fall interface exposes the RSSI heatmap."""
from pathlib import Path


def test_fall_ui_has_heatmap_and_export():
    src = (Path(__file__).resolve().parents[1] / "dashboard.py").read_text()
    assert "◉ Coverage + heatmap" in src
    assert "'● Coverage points', '🌡 RSSI heatmap'" in src
    assert "view='heatmap'" in src
    assert "points_on_heat=show_heat_dots" in src
    assert "Download RSSI heatmap (HTML)" in src


def test_exported_heatmap_contains_interactive_plot(tmp_path):
    from rf_core import simulate_rows, write_rows
    from coverage_map import create_map
    saved = write_rows(simulate_rows(30), tmp_path/'readings.csv')
    html = create_map(saved, tmp_path/'heat.html', view='heatmap')
    content = html.read_text()
    assert 'Plotly.newPlot' in content
    assert 'SIMULATED RF' in content
    assert 'Illustrative interpolation' in content
