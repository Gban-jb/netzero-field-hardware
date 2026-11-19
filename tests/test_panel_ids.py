"""Verify Excel-extracted names and mapping without inventing surveyed panel GPS."""
import pandas as pd
from rf_core import simulate_rows
from panel_overlay import load_panel_catalog, map_to_panel_rows, attach_panel_labels, panel_figure


def test_source_catalog_has_real_excel_cells_and_excludes_gap():
    catalog=load_panel_catalog()
    assert len(catalog)==2538
    assert catalog.panel_id.nunique()==2538
    assert set(catalog.row_id)==set('ABCDEFGHIJKLMNOP')
    assert set(catalog.tier)=={'T','B'}
    assert 'E-082-T' not in set(catalog.panel_id)
    assert 'E-082-B' not in set(catalog.panel_id)
    assert catalog.loc[catalog.panel_id.eq('A-001-T'),'excel_number_cell'].iloc[0]=='C9'
    assert catalog.loc[catalog.panel_id.eq('P-081-B'),'excel_number_cell'].iloc[0]=='OA81'
    assert set(catalog.position_type)=={'SCHEMATIC_PIXEL_ONLY'}


def test_synthetic_reading_assigns_both_candidates_and_preserves_coordinates():
    d=pd.DataFrame(simulate_rows(50))
    got=attach_panel_labels(d)
    assert len(got)==len(d)
    assert got.latitude.equals(d.latitude)
    assert got.longitude.equals(d.longitude)
    assert got.value.equals(d.value)
    assert got.panel_id_top.notna().all()
    assert got.panel_id_bottom.notna().all()
    assert got.panel_id_top.str.endswith('-T').all()
    assert got.panel_id_bottom.str.endswith('-B').all()
    assert set(got.panel_id_top).issubset(set(load_panel_catalog().panel_id))
    assert 'NOT DISTINGUISHED' in got.panel_match_note.iloc[0]


def test_panel_hover_and_search_highlight():
    d=pd.DataFrame(simulate_rows(20))
    fig,n=panel_figure(d,view='coverage',show_labels=True,highlight_panel='P-081-B')
    assert n==20
    assert len(fig.layout.images)==1
    names=[str(t.name) for t in fig.data]
    assert 'Selected Excel panel' in names
    assert 'Excel panel catalog' in names
    catalog_trace=[t for t in fig.data if t.name=='Excel panel catalog'][0]
    assert len(catalog_trace.x)==2538
    highlight=[t for t in fig.data if t.name=='Selected Excel panel'][0]
    assert highlight.text[0]=='P-081-B'
    assert any('Nearest drawing pair' in str(t.hovertext) for t in fig.data if t.hovertext is not None)


def test_unmapped_gps_remains_unmapped():
    d=pd.DataFrame(simulate_rows(4)).drop(columns=['layout_x','layout_y'])
    got=attach_panel_labels(d)
    assert got.panel_id_top.isna().all()
    assert got.panel_id_bottom.isna().all()
    assert len(got)==4
