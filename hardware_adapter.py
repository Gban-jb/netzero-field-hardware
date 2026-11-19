"""Explicit real-hardware integration contract. No invented live HackRF or GPS support."""
from dataclasses import dataclass
from datetime import datetime, timezone
from rf_core import FREQUENCY_HZ
@dataclass
class RFReading:
    timestamp_utc: str
    latitude: float
    longitude: float
    value: float  # dBm only if the instrument provides/calibration supports it
    receiver_id: str
    source: str
    frequency_hz: int = FREQUENCY_HZ

class HardwareNotConfigured(RuntimeError): pass

def get_live_reading():
    # TODO 1: Connect GPS receiver and verify fix and NMEA coordinates.
    # TODO 2: Select receiver: Wi-Fi adapter for RSSI, or HackRF for spectrum/power.
    # TODO 3: For Wi-Fi RSSI, log driver-provided dBm at the correct 5 GHz channel.
    # TODO 4: For HackRF, capture IQ or power-spectrum with installed native driver;
    #    HackRF raw FFT amplitudes are NOT automatically calibrated dBm or Wi-Fi RSSI.
    # TODO 5: Timestamp, receiver ID, actual tuned center frequency, calibrated units,
    #    GPS lock status, and source='REAL'; append through rf_core.write_rows.
    # TODO 6: Validate permissible frequencies/regional device support, operator safety.
    raise HardwareNotConfigured('Live hardware not configured: integrate GPS + Wi-Fi adapter or calibrated SDR reader first.')
