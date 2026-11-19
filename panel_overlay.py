"""Plot RF demo samples over the supplied solar-array drawing (not georeferenced GPS).

The project engineering plan has NO per-module surveyed coordinates. `layout_x` and
`layout_y` in the demo CSV are synthetic route positions in [0, 1]. This module
places those demo positions along drawn panel rows, for a clearly labelled visual
DEMONSTRATION. It deliberately never uses fabricated lat/lon to align a point.
Real measurements require approved surveyed panel positions / image calibration.
"""
from __future__ import annotations
from pathlib import Path
from functools import lru_cache
import numpy as np
import pandas as pd
from PIL import Image
import plotly.graph_objects as go
from rf_core import ROOT, temperature_flags

IMAGE = ROOT / 'assets' / 'site_panels_crop.png'
PANEL_CATALOG = ROOT / 'data' / 'panel_catalog.csv'
# Original drawing crop (in pixels): x 105..1062, y 294..706.
CROP_LEFT, CROP_TOP = 105, 294
# Approximate drawn panel rows: (row center y, (x start, x end) segments).
# These coordinates describe the illustration, not actual survey coordinates.
ROWS = [
    (334, ((138, 711), (744, 1030))),
    (370, ((138, 711), (744, 1030))),
    (407, ((138, 711), (744, 1030))),
    (445, ((138, 711), (744, 1030))),
    (481, ((138, 711), (744, 1030))),
    (518, ((138, 567), (744, 1030))),
    (555, ((599, 1030),)),
    (592, ((599, 1030),)),
    (629, ((599, 1030),)),
    (666, ((599, 1030),)),
]
STATUS_COLORS = {
    'Weak + hot': '#7C3AED', 'Weak RSSI': '#C2414B',
    'Hot only': '#D97706', 'High RSSI': '#2563B8',
    'Normal RSSI': '#16836B',
}


@lru_cache(maxsize=1)
def load_panel_catalog() -> pd.DataFrame:
    """Read labels extracted from the supplied 'SOLAR FARM' Excel diagram.

    Each numbered Excel cell is associated with a T (top) and B (bottom)
    location. These are reference *drawing* positions, not WGS84 coordinates.
    """
    catalog = pd.read_csv(PANEL_CATALOG)
    if len(catalog) != 2538 or catalog.panel_id.nunique() != 2538:
        raise ValueError('Panel catalog is incomplete; rebuild from the provided Excel diagram.')
    return catalog


def attach_panel_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Keep every reading and add the nearest *illustrative* drawing panel pair.

    A synthetic route has a panel-row centerline, not enough detail to choose
    an individual top/bottom module. Report BOTH candidate module IDs rather
    than claiming a unique per-panel GPS position.
    """
    result = df.copy()
    mapped = map_to_panel_rows(result)
    names = ['panel_row', 'panel_number', 'panel_pair_label', 'panel_id_top',
             'panel_id_bottom', 'panel_match_note']
    for col in names:
        result[col] = None
        if not mapped.empty:
            result.loc[mapped.index, col] = mapped[col]
    return result


def valid_positions(df: pd.DataFrame) -> pd.DataFrame:
    """Use explicit drawing-local coordinates only; never infer from GPS values."""
    if not {'layout_x', 'layout_y'}.issubset(df.columns):
        return df.iloc[0:0].copy()
    positions = df.copy()
    positions['layout_x'] = pd.to_numeric(positions['layout_x'], errors='coerce')
    positions['layout_y'] = pd.to_numeric(positions['layout_y'], errors='coerce')
    return positions[positions.layout_x.between(0, 1) & positions.layout_y.between(0, 1)].copy()


def map_to_panel_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Map simulated layout positions to nearest EXISTING Excel module numbers.

    The row geometry matches the supplied engineering drawing; the ID catalog
    is extracted from the actual Excel cells, including the missing E-082.
    """
    df = valid_positions(df)
    if df.empty:
        return df
    catalog = load_panel_catalog()
    # Each numbered Excel cell has two T/B markers at the same x coordinate.
    pairs = {int(idx): block.sort_values('panel_px_x').reset_index(drop=True)
             for idx, block in catalog[catalog.tier.eq('T')].groupby('physical_row_index')}
    xs, ys, physical_rows = [], [], []
    panel_rows, panel_nums, panel_pairs, tops, bottoms = [], [], [], [], []
    for row in df.itertuples():
        v = float(np.clip((row.layout_y - .08) / .825, 0, .999999))
        row_idx = min(len(ROWS)-1, int(v * len(ROWS)))
        center_y, parts = ROWS[row_idx]
        lengths = [right - left for left, right in parts]
        at = float(np.clip(row.layout_x, 0, 1)) * sum(lengths)
        absolute_x = parts[-1][1]
        for (left, right), length in zip(parts, lengths):
            if at <= length:
                absolute_x = left + at
                break
            at -= length
        x = absolute_x - CROP_LEFT
        row_catalog = pairs[row_idx]
        pick = int(np.argmin(abs(row_catalog.panel_px_x.to_numpy(float) - x)))
        match = row_catalog.iloc[pick]
        letter = str(match.row_id)
        number = int(match.panel_number)
        top = str(match.panel_id)
        bottom = top[:-1] + 'B'
        xs.append(x)
        ys.append(center_y - CROP_TOP)
        physical_rows.append(row_idx)
        panel_rows.append(letter)
        panel_nums.append(number)
        panel_pairs.append(f'{letter}-{number:03d} (T/B)')
        tops.append(top)
        bottoms.append(bottom)
    df['panel_px_x'] = xs
    df['panel_px_y'] = ys
    df['physical_row_index'] = physical_rows
    df['panel_row'] = panel_rows
    df['panel_number'] = panel_nums
    df['panel_pair_label'] = panel_pairs
    df['panel_id_top'] = tops
    df['panel_id_bottom'] = bottoms
    df['panel_match_note'] = 'NEAREST SCHEMATIC PAIR; T/B NOT DISTINGUISHED'
    return df


def _panel_mask(xx, yy):
    mask = np.zeros(xx.shape, dtype=bool)
    for center, parts in ROWS:
        ry = center - CROP_TOP
        for left, right in parts:
            mask |= (np.abs(yy - ry) <= 12) & (xx >= left-CROP_LEFT) & (xx <= right-CROP_LEFT)
    return mask


def _heat_data(df, width, height):
    """A local, masked inverse-distance estimate; gaps without samples stay clear."""
    x = np.linspace(0, width, 180)
    y = np.linspace(0, height, 80)
    xx, yy = np.meshgrid(x, y)
    vx = df.panel_px_x.to_numpy(float)
    vy = df.panel_px_y.to_numpy(float)
    vals = df.value.to_numpy(float)
    d2 = (xx[..., None] - vx)**2 + (yy[..., None] - vy)**2
    weights = np.exp(-d2 / (2 * 34.0**2))
    mean = (weights @ vals) / np.maximum(weights.sum(axis=2), 1e-10)
    within_sample_distance = d2.min(axis=2) <= 62**2
    mean[~(_panel_mask(xx, yy) & within_sample_distance)] = np.nan
    return x, y, mean


def _color_scale(weak, high):
    """Use the weak-RSSI threshold as the key color boundary.

    Normal signals roughly 12 dBm above the weak threshold appear green;
    exceptionally high values are still separately flagged on the dot view.
    """
    lo, hi = -100.0, -20.0
    at = lambda value: float(np.clip((value - lo)/(hi-lo), 0, 1))
    a = at(weak)
    b = at(weak + 6)
    c = at(weak + 14)
    return [(0, '#EB4343'), (a, '#EB4343'),
            (b, '#F6CA50'), (c, '#2DBD71'), (1, '#2DBD71')]


def panel_figure(df, weak=-75, high=-45, temperature=35, view='coverage',
                 points_on_heat=False, show_labels=True, highlight_panel=None):
    """Plot simulated RSSI on the drawing with real Excel-derived panel IDs.

    All 2,538 positions are hover-searchable. Synthetic readings show their
    nearest numbered T/B pair; they do NOT establish either module's GPS.
    """
    if view not in ('coverage', 'heatmap'):
        raise ValueError('view must be coverage or heatmap')
    df = map_to_panel_rows(df)
    if df.empty:
        return None, 0
    df = temperature_flags(df, temperature, weak, high)
    df['point_class'] = np.select(
        [df.combined_review_flag, df.weak_rf_flag, df.high_temperature_flag, df.high_rssi_flag],
        ['Weak + hot', 'Weak RSSI', 'Hot only', 'High RSSI'],
        default='Normal RSSI')
    with Image.open(IMAGE) as pil:
        background = pil.convert('RGB')
    width, height = background.size
    fig = go.Figure()
    fig.add_layout_image(dict(source=background, xref='x', yref='y',
                              x=0, y=height, sizex=width, sizey=height,
                              xanchor='left', yanchor='top',
                              sizing='stretch', layer='below', opacity=1.0))
    if view == 'heatmap':
        x, y, z = _heat_data(df, width, height)
        fig.add_trace(go.Heatmap(x=x, y=height-y, z=z, zmin=-100, zmax=-20,
                                 colorscale=_color_scale(weak, high),
                                 opacity=.65, connectgaps=False,
                                 hovertemplate='Estimated RSSI: %{z:.1f} dBm<extra>Illustrative interpolation</extra>',
                                 colorbar=dict(title=dict(text='RSSI (dBm)', font=dict(color='#18324F')),
                                               tickvals=[-95, weak, high, -20], len=.75, thickness=17,
                                               tickfont=dict(color='#18324F'))))
    # Each original Excel position is available for lookup, including when
    # no synthetic reading is near it. Pale markers avoid obscuring the plan.
    catalog = load_panel_catalog()
    fig.add_trace(go.Scatter(
        x=catalog.panel_px_x, y=height-catalog.panel_px_y,
        mode='markers', name='Excel panel catalog', showlegend=False,
        text=catalog.panel_id,
        customdata=catalog[['excel_number_cell','row_id']].to_numpy(),
        hovertemplate='<b>Panel %{text}</b><br>Excel cell: %{customdata[0]}'
                      '<br>Row: %{customdata[1]}<br>Drawing position only; no verified panel GPS'
                      '<extra>Excel panel catalog</extra>',
        marker=dict(size=4, color='#1E3A8A', opacity=.11),
    ))
    if view == 'coverage' or points_on_heat:
        rendered_names = set()
        for label in STATUS_COLORS:
            subset = df[df.point_class == label]
            if subset.empty:
                continue
            hover = [
                f'<b>Nearby Excel pair: {r.panel_id_top} / {r.panel_id_bottom}</b>'
                f'<br>Excel row: {r.panel_row}; position: {int(r.panel_number)}'
                f'<br><b>RSSI: {r.value:.1f} dBm</b>'
                f'<br>Synthetic latitude: {r.latitude:.6f}'
                f'<br>Synthetic longitude: {r.longitude:.6f}'
                f'<br>Type: {label}<br>Survey: {r.survey_id}'
                f'<br>Source: {r.source}'
                f'<br>Temperature: {r.temperature_c if pd.notna(r.temperature_c) else "N/A"} °C'
                f'<br><i>Nearest drawing pair; top/bottom not resolved</i>'
                for r in subset.itertuples()
            ]
            text_labels=[]
            for r in subset.itertuples():
                short=f'{r.panel_row}-{int(r.panel_number):03d}'
                text_labels.append(short if short not in rendered_names else '')
                rendered_names.add(short)
            custom = subset[['latitude','longitude','panel_id_top','panel_id_bottom']].to_numpy()
            fig.add_trace(go.Scatter(
                x=subset.panel_px_x, y=height-subset.panel_px_y,
                mode='markers+text' if show_labels else 'markers',
                name=label, text=text_labels if show_labels else None,
                textposition='top center', textfont=dict(size=9, color='#15324F'),
                customdata=custom, hovertext=hover,
                hovertemplate='%{hovertext}<extra></extra>',
                marker=dict(color=STATUS_COLORS[label], size=9 if view=='coverage' else 5,
                            line=dict(color='#FFFFFF', width=1.4), opacity=.94),
            ))
    if highlight_panel:
        match=catalog[catalog.panel_id == highlight_panel]
        if not match.empty:
            r=match.iloc[0]
            fig.add_trace(go.Scatter(
                x=[r.panel_px_x], y=[height-r.panel_px_y],
                mode='markers+text', name='Selected Excel panel',
                text=[r.panel_id], textposition='bottom center',
                textfont=dict(size=14, color='#172B55'),
                hovertemplate=f'<b>{r.panel_id}</b><br>Excel cell {r.excel_number_cell}'
                              '<br>No verified individual-panel GPS<extra>Selected panel</extra>',
                marker=dict(symbol='circle-open', size=22,
                            line=dict(width=4, color='#E11D48'), color='#FFFFFF'),
            ))
    # Placement of transmitter/receiver is proposed rather than GPS-surveyed.
    for x_pos, label, color in [(26, 'Tx (proposed)', '#1D4ED8'),
                                (width-24, 'Rx (proposed)', '#1D4ED8')]:
        fig.add_annotation(x=x_pos, y=32, text=label, showarrow=False,
                           font=dict(size=11, color='white'), bgcolor=color,
                           bordercolor='white', borderwidth=1, borderpad=4)
    fig.update_layout(
        title=dict(text=('Excel-labelled RF samples on solar drawing — illustrative'
                         if view=='coverage' else
                         'Excel-labelled signal heatmap — illustrative estimate'),
                   font=dict(size=16, color='#18324F'), x=.02),
        height=545, paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF',
        font=dict(color='#18324F'),
        margin=dict(l=15, r=55 if view=='heatmap' else 20, t=65, b=20),
        legend=dict(orientation='h', y=-.04, x=.01, font=dict(size=10)),
        hovermode='closest', hoverdistance=6,
        annotations=[*fig.layout.annotations,
                     dict(text='SIMULATED RF/GPS • EXCEL PANEL IDs • NOT GEOREFERENCED',
                          x=.5, y=1.04, xref='paper', yref='paper',
                          showarrow=False, font=dict(size=10, color='#B42332'))],
    )
    fig.update_xaxes(range=[0, width], visible=False, fixedrange=False)
    fig.update_yaxes(range=[0, height], visible=False, fixedrange=False,
                     scaleanchor='x', scaleratio=1)
    return fig, len(df)
