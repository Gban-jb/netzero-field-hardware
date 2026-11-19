"""Shared data schema, validation, simulated logging, and RF analysis."""
from __future__ import annotations
import csv
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
DEFAULT_CSV = DATA / 'measurements.csv'
FREQUENCY_HZ = 5_180_000_000
FREQUENCY_GHZ = 5.180
CHANNEL = 36
PANEL_COUNT = 2538
STRING_COUNT = 94
PANELS_PER_STRING = 27
INVERTER_COUNT = 8
PV_KW_DC = 1383.21
SITE_LAT_FROM_PLAN = 34 + 47/60 + 9.70/3600
# Longitude below is NOT specified by the drawing. This is a fabricated demo-only anchor.
DEMO_LONGITUDE = -86.5720
FIELDS = ['timestamp_utc','latitude','longitude','measurement_type','value','units','frequency_hz','wifi_channel','receiver_id','source','gps_lock','survey_id','zone_id','layout_x','layout_y','hardware_status','temperature_c','temperature_source','transmitter_side','receiver_side']
ZONES = ['Northwest','North-central','Northeast','Southwest','South-central','Southeast']

def simulate_rows(count=120, seed=42, survey_id='Demo A', start=None):
    """Deterministic synthetic route over a six-zone *schematic*, not field GPS."""
    if count < 1: raise ValueError('count must be at least 1')
    rng = random.Random(seed)
    start = start or datetime(2026,11,9,15,0,tzinfo=timezone.utc)
    rows=[]
    for i in range(count):
        # Serpentine paths, two array blocks separated by an access corridor.
        t = i / max(1,count-1)
        band = min(11,int(t*12))
        within = t*12-band
        x = (0.06 + 0.88*(within if band%2==0 else 1-within))
        y = 0.08 + band*0.075
        # x/y schematic; GPS coordinates are illustrative, NOT true array geolocation.
        lat = SITE_LAT_FROM_PLAN + (y-.5)*0.0018
        lon = DEMO_LONGITUDE + (x-.5)*0.0034
        zone = ('North' if y >= .52 else 'South') + ('west' if x<.34 else 'east' if x>.66 else '-central')
        # Normalize to readable zone names.
        zone = ('North' if y>=.52 else 'South') + ('west' if x<.34 else 'east' if x>.66 else '-central')
        base = -61 - (13 if x>.70 else 0) - (10 if y>.74 else 0)
        reading = max(-98,min(-38,round(base+rng.gauss(0,7),1)))
        rows.append(dict(timestamp_utc=(start+timedelta(seconds=i*8)).isoformat(), latitude=round(lat,7),longitude=round(lon,7),measurement_type='Wi-Fi RSSI',value=reading,units='dBm',frequency_hz=FREQUENCY_HZ,wifi_channel=CHANNEL,receiver_id='demo-receiver-01',source='SIMULATED',gps_lock=True,survey_id=survey_id,zone_id=zone,layout_x=round(x,4),layout_y=round(y,4),hardware_status='SIMULATED — NO RECEIVER',temperature_c=round(27+12*(y>.65)+rng.gauss(0,2.3),1),temperature_source='SIMULATED',transmitter_side='WEST (SCHEMATIC)',receiver_side='EAST (SCHEMATIC)'))
    return rows

def write_rows(rows, path=DEFAULT_CSV, append=False):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    mode='a' if append else 'w'
    with path.open(mode,newline='',encoding='utf-8') as fp:
        writer=csv.DictWriter(fp,fieldnames=FIELDS,extrasaction='ignore')
        if not append or fp.tell()==0: writer.writeheader()
        writer.writerows(rows)
    return path

def load_csv(path=DEFAULT_CSV):
    df=pd.read_csv(path)
    needed={'latitude','longitude','value','source','timestamp_utc'}
    missing=needed-set(df.columns)
    if missing: raise ValueError('CSV missing required columns: '+', '.join(sorted(missing)))
    for col in ('latitude','longitude','value','layout_x','layout_y','frequency_hz','temperature_c'):
        if col in df: df[col]=pd.to_numeric(df[col],errors='coerce')
    df=df.dropna(subset=['latitude','longitude','value']).copy()
    df=df[df['latitude'].between(-90,90)&df['longitude'].between(-180,180)&df['value'].between(-150,30)].copy()
    if 'survey_id' not in df: df['survey_id']='Imported survey'
    if 'zone_id' not in df: df['zone_id']='Unassigned'
    if 'measurement_type' not in df: df['measurement_type']='RSSI'
    if 'frequency_hz' not in df: df['frequency_hz']=float('nan')
    if 'gps_lock' not in df: df['gps_lock']='unknown'
    if 'temperature_c' not in df: df['temperature_c']=float('nan')
    if 'temperature_source' not in df: df['temperature_source']='NOT PROVIDED'
    return df.reset_index(drop=True)

def summarize(df,threshold=-75):
    if df.empty: return {'samples':0,'weak':0,'weak_pct':0,'avg':None,'min':None,'max':None}
    vals=df['value']; weak=int((vals<threshold).sum())
    return dict(samples=len(df),weak=weak,weak_pct=round(100*weak/len(df),1),avg=round(float(vals.mean()),1),min=round(float(vals.min()),1),max=round(float(vals.max()),1))

def zones_summary(df,threshold=-75,min_samples=5):
    if df.empty: return pd.DataFrame(columns=['zone_id','samples','avg_dbm','weak_count','weak_pct','alert'])
    out=df.groupby('zone_id',dropna=False).agg(samples=('value','size'),avg_dbm=('value','mean'),weak_count=('value',lambda x:int((x<threshold).sum()))).reset_index()
    out['weak_pct']=(100*out.weak_count/out.samples).round(1)
    out['avg_dbm']=out.avg_dbm.round(1)
    out['alert']=(out.samples>=min_samples)&(out.weak_pct>=40)
    return out.sort_values(['alert','weak_pct'],ascending=False)

def comparison(df):
    """Area-level comparison only; does not imply repeated sample location matching."""
    x=df.groupby(['survey_id','zone_id'],dropna=False)['value'].agg(['size','mean']).reset_index()
    return x.rename(columns={'size':'samples','mean':'avg_dbm'})


def temperature_flags(df, temperature_threshold_c=35.0, weak_threshold_dbm=-75.0, high_rssi_threshold_dbm=-45.0):
    """Flag RF readings paired with high measured ambient temperature; no causal inference."""
    result=df.copy()
    result['temperature_c']=pd.to_numeric(result['temperature_c'], errors='coerce')
    result['high_temperature_flag']=result['temperature_c'].gt(temperature_threshold_c)
    result['weak_rf_flag']=result['value'].lt(weak_threshold_dbm)
    result['high_rssi_flag']=result['value'].gt(high_rssi_threshold_dbm)
    result['combined_review_flag']=result['high_temperature_flag'] & result['weak_rf_flag']
    return result

def filter_day(df, selected_date):
    dates=pd.to_datetime(df['timestamp_utc'],utc=True,errors='coerce').dt.date
    return df.loc[dates==selected_date].copy()
