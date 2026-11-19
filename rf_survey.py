"""Generate labelled simulation data or validate an imported real-world CSV."""
import argparse
from pathlib import Path
from rf_core import DEFAULT_CSV, simulate_rows, write_rows, load_csv

def main():
    p=argparse.ArgumentParser(description='Student 4 RF/GPS survey logger — simulated mode only')
    p.add_argument('--mode',choices=['simulate','validate'],default='simulate')
    p.add_argument('--samples',type=int,default=120)
    p.add_argument('--seed',type=int,default=42)
    p.add_argument('--output',type=Path,default=DEFAULT_CSV)
    p.add_argument('--survey-id',default='Demo A')
    p.add_argument('--append',action='store_true')
    args=p.parse_args()
    if args.mode=='validate':
        df=load_csv(args.output);print(f'Validated {len(df)} rows from {args.output}');return
    if args.samples<1: p.error('--samples must be positive')
    rows=simulate_rows(args.samples,args.seed,args.survey_id)
    dest=write_rows(rows,args.output,append=args.append)
    print(f'Wrote {len(rows)} SIMULATED observations to {dest}; no real receiver/GPS was used.')
if __name__=='__main__': main()
