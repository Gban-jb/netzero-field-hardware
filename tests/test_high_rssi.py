import pandas as pd
from rf_core import temperature_flags

def test_high_rssi_strictly_above_threshold():
    d=pd.DataFrame({'value':[-85,-75,-60,-45,-35],'temperature_c':[22,22,22,22,22]})
    r=temperature_flags(d,35,-75,-45)
    assert r.high_rssi_flag.tolist()==[False,False,False,False,True]
    assert r.weak_rf_flag.tolist()==[True,False,False,False,False]
