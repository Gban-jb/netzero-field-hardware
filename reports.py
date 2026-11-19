"""Offline CSV/JSON summary exports from collected data."""
import argparse
import json
from pathlib import Path
from rf_core import ROOT, DEFAULT_CSV, load_csv, summarize, zones_summary

def generate(path=DEFAULT_CSV, out=ROOT/'outputs', threshold=-75, minimum=5):
    df=load_csv(path);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    zone=zones_summary(df,threshold,minimum)
    zone.to_csv(out/'zone_report.csv',index=False)
    s=summarize(df,threshold)
    report={'status':'SIMULATED demo' if (df.source.astype(str).str.upper()=='SIMULATED').any() else 'IMPORTED RECORDS (not independently validated)','layout':'2023 submitted final solar layout reference, 2538 panels / 94 strings / 8 inverters','gps_note':'Demo geographic coordinates are not surveyed site positions','threshold_dbm':threshold,'min_samples_per_zone':minimum,'summary':s,'zone_alerts':int(zone.alert.sum()) if len(zone) else 0}
    (out/'summary_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=DEFAULT_CSV);p.add_argument('--weak-threshold',type=float,default=-75);args=p.parse_args();print(json.dumps(generate(args.input,threshold=args.weak_threshold),indent=2))
