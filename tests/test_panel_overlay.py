from pathlib import Path
import pandas as pd
from rf_core import simulate_rows, load_csv, write_rows
from panel_overlay import panel_figure, map_to_panel_rows, valid_positions
from coverage_map import create_map


def test_overlay_has_image_and_demo_points():
    df = pd.DataFrame(simulate_rows(24))
    points = map_to_panel_rows(df)
    assert len(points) == 24
    assert points.panel_px_x.between(0,957).all()
    assert points.panel_px_y.between(0,412).all()
    plot,n = panel_figure(df, view='coverage')
    assert n == 24 and len(plot.layout.images) == 1
    heat,k = panel_figure(df, view='heatmap')
    assert k == n and heat.data[0].type == 'heatmap'
    assert pd.isna(heat.data[0].z).sum() > 0  # Do not paint unsampled spaces.


def test_real_gps_alone_is_not_plotted(tmp_path):
    d = pd.DataFrame(simulate_rows(5)).drop(columns=['layout_x','layout_y'])
    fig,n = panel_figure(d)
    assert fig is None and n == 0
    p=tmp_path/'gps_without_layout.csv'
    d.to_csv(p,index=False)
    import pytest
    with pytest.raises(ValueError,match='layout_x'):
        create_map(p,tmp_path/'bad.html')


def test_offline_heatmap_export(tmp_path):
    path=write_rows(simulate_rows(35),tmp_path/'data.csv')
    out=create_map(path,tmp_path/'panel_heatmap.html',view='heatmap')
    content=out.read_text()
    assert 'SIMULATED' in content and 'Plotly.newPlot' in content
