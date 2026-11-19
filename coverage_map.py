"""Export an OFFLINE interactive panel-image coverage plot (not a GPS map)."""
import argparse
from pathlib import Path
from rf_core import DEFAULT_CSV, ROOT, load_csv
from panel_overlay import panel_figure


def create_map(input_file=DEFAULT_CSV, output_file=None, threshold=-75,
               temperature_threshold_c=35, high_rssi_threshold_dbm=-45,
               view='coverage'):
    df = load_csv(input_file)
    if df.empty:
        raise ValueError('No valid measurements in input CSV')
    fig, n = panel_figure(df, weak=threshold, high=high_rssi_threshold_dbm,
                          temperature=temperature_threshold_c, view=view)
    if not n:
        raise ValueError('No layout_x / layout_y coordinates in CSV; a drawing cannot be aligned from GPS alone.')
    output_file = Path(output_file or ROOT/'outputs' / ('panel_heatmap.html' if view=='heatmap' else 'coverage_map.html'))
    output_file.parent.mkdir(parents=True,exist_ok=True)
    fig.write_html(str(output_file),include_plotlyjs=True,full_html=True)
    return output_file


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,default=DEFAULT_CSV)
    p.add_argument('--output',type=Path,default=None)
    p.add_argument('--weak-threshold',type=float,default=-75)
    p.add_argument('--high-threshold',type=float,default=-45)
    p.add_argument('--view',choices=['coverage','heatmap'],default='coverage')
    a=p.parse_args()
    print('Saved',create_map(a.input,a.output,a.weak_threshold,35,a.high_threshold,a.view))

if __name__=='__main__': main()
