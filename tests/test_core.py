from pathlib import Path
import pytest
from rf_core import (FREQUENCY_HZ,PANEL_COUNT,STRING_COUNT,simulate_rows,write_rows,load_csv,summarize,zones_summary)
from coverage_map import create_map
from reports import generate

def test_layout_and_frequency():
    assert PANEL_COUNT==STRING_COUNT*27==2538
    assert FREQUENCY_HZ==5_180_000_000

def test_synthetic_replay_and_threshold(tmp_path):
    rows=simulate_rows(50,seed=4)
    assert len(rows)==50 and all(x['source']=='SIMULATED' for x in rows)
    assert all(x['frequency_hz']==FREQUENCY_HZ for x in rows)
    p=write_rows(rows,tmp_path/'measurements.csv')
    df=load_csv(p)
    s=summarize(df,-75)
    assert s['samples']==50 and s['weak']>=0
    z=zones_summary(df,-75,5)
    assert z.samples.sum()==50

def test_exports(tmp_path):
    p=write_rows(simulate_rows(30),tmp_path/'measurements.csv')
    html=create_map(p,tmp_path/'coverage_map.html')
    assert html.exists() and 'SIMULATED' in html.read_text()
    rpt=generate(p,tmp_path/'reports')
    assert rpt['summary']['samples']==30
    assert (tmp_path/'reports'/'zone_report.csv').exists()

def test_bad_schema_rejected(tmp_path):
    p=tmp_path/'bad.csv';p.write_text('value\n-70\n')
    with pytest.raises(ValueError,match='missing required columns'):load_csv(p)
