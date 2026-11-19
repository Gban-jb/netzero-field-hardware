from datetime import date
from rf_core import simulate_rows,write_rows,load_csv,temperature_flags,filter_day

def test_temperature_and_history(tmp_path):
    p=write_rows(simulate_rows(35),tmp_path/'data.csv')
    df=load_csv(p)
    flags=temperature_flags(df,35,-75)
    assert len(flags)==35
    assert flags.combined_review_flag.equals(flags.high_temperature_flag & flags.weak_rf_flag)
    assert len(filter_day(df,date(2026,11,9)))==35

def test_missing_temperature_is_not_hot(tmp_path):
    p=write_rows(simulate_rows(5),tmp_path/'data.csv')
    import pandas as pd
    d=pd.read_csv(p).drop(columns=['temperature_c','temperature_source'])
    d.to_csv(p,index=False)
    df=load_csv(p)
    assert not temperature_flags(df).high_temperature_flag.any()
