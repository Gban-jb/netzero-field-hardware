# netzero-field-hardware

**Student 4 — Field Hardware, Positioning & Connectivity**
Alabama A&M University · Net Zero Solar Electric Initiative
Author: **Armaan Asim** ([@Armaaaaannnn](https://github.com/Armaaaaannnn))

This workstream covers GPS/RTK positioning, Wi-Fi and RF survey, and the
dashboard that turns recorded readings into coverage maps and heatmaps.
The project portal links here from the
[RF & Positioning page](https://netzero-solar-portal.vercel.app/departments/engineering/students/student-4).

## Run it locally

```bash
python -m pip install -r requirements.txt
python run_kit.py
```

`run_kit.py` generates a sample survey if none exists, builds the coverage
map, the heatmap and the summary report, then opens the Streamlit
dashboard. Everything it writes lands in `outputs/`, which is regenerated
on each run and therefore not tracked in git.

## Layout

| Path | What it holds |
| --- | --- |
| `dashboard.py` | Streamlit entry point — the Fall-only view |
| `dashboard_advanced.py` | The fuller dashboard the Fall view builds on |
| `rf_core.py`, `rf_survey.py` | Survey data model, loading and simulation |
| `coverage_map.py`, `panel_overlay.py` | Coverage map and RSSI heatmap rendering |
| `hardware_adapter.py`, `live_status.py` | Interface to the physical kit |
| `reports.py` | Offline CSV and JSON exports |
| `data/` | Recorded measurements and the panel catalogue |
| `docs/` | Demo guide, hardware integration notes, site layout reference |
| `tests/` | pytest suite |
| `outputs/` | Generated maps and reports — not tracked |

Run the tests with `python -m pytest tests/`.

---

# AAMU Student 4 — Fall-only dashboard (November 2026)

**The dashboard opens in a simplified Fall-only view by default.** To launch it:

```bash
python -m pip install -r requirements.txt
python run_kit.py
```

The five tabs are (the fourth now includes both the coverage map and heatmap):

1. **GPS + RF:** latest recorded latitude, longitude, UTC time and RSSI (demo values are visibly marked as simulated).
2. **Live status:** start, stop, simulate sensor disconnection and reconnect; mock samples are appended to a real CSV file every ~2 seconds.
3. **CSV logger:** view latest stored records and download the timestamped readings.
4. **Coverage + heatmap:** two sub-tabs: **Coverage points** shows named Excel panel IDs and weak-signal dots, while **RSSI heatmap** overlays estimated red/yellow/green signal strength on the same drawing. Both export to offline HTML; unsampled areas remain visible.
5. **Replay + export:** select a recorded session, move the sample-by-sample playback slider, inspect the plotted route and export CSV/summary files.

**Important:** This software is an illustrative prototype. The built-in values (RSSI, GPS and panel proximity) are synthetic and not a live field measurement. The physical RF/GPS kit, hardware driver integration, actual GPS fixes, physical sensor disconnect/reconnect test and 30 authorized field samples are **not yet complete**. Do not present software-only simulation as final physical-kit acceptance.

In **Coverage + heatmap**, select **RSSI heatmap** to see the color overlay; toggle **Show measurement dots on the heatmap** to see survey points. Use **Download RSSI heatmap (HTML)** to open the exported result without running Streamlit. Both views use schematic panel locations and synthetic radio readings, not verified field coverage.

To see the previous full dashboard with additional Spring-style features, run:

```bash
python -m streamlit run dashboard_advanced.py
```

- `dashboard.py` is the default **Fall-only** interface.
- `dashboard_advanced.py` preserves the earlier multi-tab dashboard and its historical analysis features.
- The supplied panel names remain searchable and linked to schematic diagram positions, not surveyed individual module GPS coordinates.
- If you have real field records in your CSV, **back them up before clicking Demo A**, which replaces the CSV at the chosen path.

For a short demonstration script, see `docs/FALL_DEMO_GUIDE.md`.

---

## Notes about the original full dashboard

# Excel panel names integrated into the RF coverage dashboard

**Update: 17 November 2026.** The panel management workbook supplied with this project is incorporated in `docs/Solar Panel Management Diagram 9-9-2025.xlsx`. Its **2,538 derived module IDs (A–P, number, T/B)** and their estimated drawing positions are exported as `data/panel_catalog.csv`. **No numbers absent from Excel are invented (for example E-082 is missing).**

In the **Panel coverage + heatmap** tab, every module can be identified by hover or the search-and-highlight control; RF measurement dots carry the nearest **top/bottom candidate pair** and the original **synthetic** coordinates. The map can display panel-number labels beside RF dots, the original RSSI plots have panel-pair hover labels, and the export tab includes the full panel catalog and sample-to-pair CSV. Open `outputs/coverage_map.html` for an offline interactive map, or `outputs/panel_heatmap.html` for the updated heatmap.

**Accuracy:** Excel provides names and layout, not surveyed individual module coordinates. All RF/GPS values are simulated. The per-reading panel matches are nearest *diagram positions*, not verified physical locations. See **[docs/PANEL_ID_MAPPING.md](docs/PANEL_ID_MAPPING.md)** for the precise extraction/mapping rules and limitations.

---

# AAMU Student 4 — Solar RF / Communications Dashboard

**One clean Streamlit dashboard** for the RF/GPS survey kit of Dr. Yaqub's solar project. Includes actual provided *final* site layout reference (not a surveyed GIS layer), demo measurement CSV, simulated field logger, panel-image coverage points and a signal heatmap, RSSI chart, zone alerts, two-session comparison, exports, and clearly identified HackRF/GPS connection hooks.

## Quick start (Windows / macOS / Linux)

Install Python 3.10+ and open a terminal in this folder:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python run_kit.py
# macOS/Linux instead:
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run_kit.py
```

Open http://localhost:8501 (usually opens automatically). Stop with Ctrl+C. **Do not double-click a Python file to launch Streamlit directly.** To change ports: `.venv/bin/python -m streamlit run dashboard.py --server.port 8502` (use `.venv\Scripts\python` on Windows).

Alternatively launch `python -m streamlit run dashboard.py`. Old entry point `live_status.py` is kept as a compatibility wrapper.

## What to demonstrate

1. Open **Overview**, show panel count **2,538**, 94 strings, eight inverters, plus original site-plan image.
2. On **Panel coverage + heatmap**, open **Coverage points** to show signal samples on the actual engineering drawing of the panels, then open **Signal strength heat map** to show estimated red/yellow/green signal regions directly on the same image. These positions are **illustrative demo positions**, NOT real readings aligned by GPS.
3. On **Signals & trends**, explain RSSI over sample index, distribution, center frequency **5.180 GHz = 5,180,000,000 Hz**, Wi-Fi channel **36**.
4. In sidebar adjust weak threshold; point out zone alerts require a minimum count and 40% weak samples.
5. Click **Add B** to append a second *simulated* session, then open **Survey comparison** and compare average RSSI by demo zone.
6. Open **Hardware & exports**, download CSV, produce report. Explain live GPS/HackRF logging requires physical kit and driver integration.

## Project files

- `dashboard.py`: unified modern interface (all features in one place)
- `rf_core.py`: shared schema, simulation, validation and analytics
- `rf_survey.py`: demo route logger; `--samples` and `--seed` CLI options
- `coverage_map.py`: exportable offline HTML panel-image point map and heatmap
- `panel_overlay.py`: image-backed Plotly overlays; demo-only panel-row alignment and masked interpolation
- `assets/site_panels_crop.png`: cropped view of drawn panel rows used as the map background
- `reports.py`: zone CSV + JSON report
- `hardware_adapter.py`: explicitly unfinished real hardware driver integration interface
- `run_kit.py`: creates maps/summary and starts Streamlit
- `data/measurements.csv`: reproducible demo A & B samples
- `assets/site_plan_page4.png`: rendered engineering site plan
- `docs/Final_Solar_Layout_Reference.pdf`: unaltered source design provided by project team
- `docs/HARDWARE_INTEGRATION.md`: real-hardware data hookup steps
- `docs/PROJECT_STATUS.md`: accurate requirements / limitations
- `tests/`: automated validation and export tests

## Generate/replay data

```bash
python rf_survey.py --mode simulate --samples 120 --seed 42 --output data/measurements.csv
python rf_survey.py --mode simulate --samples 120 --seed 99 --survey-id "Demo B" --append --output data/measurements.csv
python coverage_map.py --input data/measurements.csv
python coverage_map.py --input data/measurements.csv --view heatmap
python reports.py --input data/measurements.csv
python -m pytest -q
```

To use your own already-collected CSV, update the **CSV file** location in the sidebar. Required columns: `timestamp_utc`, `latitude`, `longitude`, `value`, `source`. For RSSI interpretation, `value` must be actual Wi-Fi RSSI **in dBm**; do **not** label arbitrary SDR FFT values dBm. Recommended extra columns: `measurement_type,units,frequency_hz,wifi_channel,receiver_id,gps_lock,survey_id,zone_id`.

## Critical data limitations

**SIMULATION, NOT FIELD RESULTS:** all shipped point lat/lon and RSSI readings are fabricated; the example longitude is not provided by the drawing. The site plan confirms panel arrangement and hardware counts but does **not** have per-panel georeferenced corners, inverter GPS coordinates or verified route/GPS boundaries. The panel map is drawn using `layout_x` and `layout_y` demonstration coordinates, **never** using fabricated GPS coordinates to align sample dots. The new color heatmap makes a masked local interpolation ONLY around illustrative samples on the drawn panel rows. These positions are not surveyed or validated, and the heatmap is not evidence of real RF conditions. In the future use actual GPS readings and proper georeferencing of site boundaries if you receive an engineering GIS/CAD survey or ground-control coordinates.

The supplied design is treated as the **final project layout by user instruction** despite the historical title block. Physical installation and actual field permissions remain separate operational questions. Hardware, calibration, 30 *real* walking route samples, live unplug/reconnect test and professor-supervised acceptance remain outstanding. This software does not make RF interference diagnoses and is passive; only collect where authorized.

## Tested in this package

CSV simulation, parsing/validation, threshold counts, zone reports, offline panel-image coverage/heatmap HTML export, and source-code compilation were tested locally (10 automated tests passed). **The Streamlit interface was not launch-tested in this packaging environment because Streamlit is not installed here.** After you install `requirements.txt` on your own computer, launch the dashboard and verify its appearance and buttons there. No online map tiles are needed: the panel drawing and all Plotly scripts are embedded in the offline HTML exports.


## November update: temperature, opposite-side setup, drone images, daily history

- **Transmitter → panel rows → receiver:** Proposed field arrangement has a transmitter and receiver on opposite sides of the panels; actual positions, antenna settings, permissions and frequency must be recorded during field setup. Prior synthetic coordinates are not actual transmitter / receiver survey positions.
- **Temperature review threshold:** Sidebar defaults to **35 °C** (adjustable 20–65 °C). `temperature_c` is optional for imported records; absent readings are never flagged as hot. Above threshold = high-temperature flag. Weak RSSI below the RSSI threshold is a separate flag; when both occur the dashboard colors the sample purple. This is correlation/review only, not proof temperature caused attenuation. Demonstration temperatures are fabricated.
- **Coverage dot colors:** teal = normal RSSI; blue = above high RSSI threshold; red = weak RSSI; orange = high temperature only; purple = weak RSSI + high temperature. **Heatmap colors:** red = weaker RSSI, yellow = moderate RSSI, green = stronger RSSI. The new heatmap interpolates ONLY schematic/demo values near drawn panel rows, leaves unsampled space transparent, and cannot be described as real measured RF coverage. Both interactive HTML files are packaged for offline use.
- **Drone snapshots:** Use the Daily history tab to upload RGB / thermal overhead images supplied by your Matrice 4TD. The user may download a ZIP containing the selected day's CSV, uploaded images, and notes. Photos are not automatically analyzed or synchronized, nor permanently stored by the web interface. Keep a real photo log and timestamp/location evidence during authorized flights. Thermal imagery is not a substitute for calibrated ambient temperature readings next to the RF receiver.
- **History:** Daily history selects any UTC date present in the current CSV; choose a date and download its records. **Important:** this is not an automatic database/backup service. Preserve actual dated CSV files and imagery in a backed-up folder, and avoid overwriting them using synthetic demo buttons.

For any REAL measured temperature, add `temperature_c` and `temperature_source` columns to the CSV, based on a calibrated/appropriate sensor and the actual sample time. Only pair RF and temperature measured closely enough in time and place to make an interpretable comparison. Never copy temperatures from the thermal image into `temperature_c` without a defensible measurement method.

### High RSSI alert (new)
Use the sidebar **High RSSI threshold (dBm)**, default **−45 dBm**. Samples strictly above this value (e.g. −35 dBm) are marked blue and counted as high RSSI flags. Weak samples below −75 dBm remain red; temperature flags stay separate. A stronger RSSI signal is not intrinsically a communications fault; compare against the approved experiment baseline. These are demonstration thresholds, not measured field calibrations.

### Solar project location

The provided AAMU engineering drawing, **AAMU-60%ISSUEDFORREVIEW-0508.pdf**, identifies the solar project at **4900 Meridian Street North, Huntsville, AL 35811, USA**. Its site-layout sheet depicts the photovoltaic array. The PDF does **not** provide enough verified georeferencing for every panel location. The map data remain marked simulated; no demo GPS position should be presented as a measured panel coordinate. `site_reference.json` records this distinction.

## November 16 update: image-backed coverage and RF heat map

The **Panel coverage + heatmap** tab now has two views:

- **Coverage points**: shows the real supplied *engineering drawing* of the panel field as a background, with simulated RSSI dot markers laid along illustrated panel rows. Colored points reflect the sidebar weak/high/temperature thresholds. Hover to see RSSI, survey, zone, and temperature.
- **Signal strength heat map**: uses the same image and blends nearby demo RSSI values into a red (weak), yellow (moderate), green (strong) heat map **only on the visible panel rows**. Unmeasured locations stay transparent. You can optionally show the underlying individual measurement dots.

The chart uses `assets/site_panels_crop.png` extracted from the engineering plan already in this ZIP. Neither plot requires an internet connection. The exported `outputs/coverage_map.html` and `outputs/panel_heatmap.html` contain the background image and Plotly JavaScript, so they can be opened offline in a browser. The original GPS fields are preserved for later genuine GPS/hardware integration, but they are **not** used to overlay points on this un-georeferenced drawing. Real data require verified field positions and a properly aligned plan; a CSV with only GPS and no `layout_x/layout_y` shows a warning rather than guessing.

Run `python run_kit.py`, then choose **Panel coverage + heatmap** in the dashboard.


### November 16 update: blue-and-white dashboard theme

The Streamlit interface now uses a clean blue-and-white university-style theme: deep blue sidebar, white content surfaces, restrained blue accents, readable navy text, and light chart backgrounds. Signal status colors remain distinct, and the red/yellow/green RF heatmap scale is intentionally preserved so weak and strong coverage are easy to interpret. The Streamlit theme is set in `.streamlit/config.toml`; the page styling is in `dashboard.py`; the panel image charts use the matching light style in `panel_overlay.py`.

## Coordinate display update (November 16, 2026)

The coverage-point view now shows the simulated latitude and longitude in each marker tooltip. Selecting a marker in the Streamlit dashboard displays the selected point coordinates below the map. The weak-coverage summary and survey-comparison graph use the same coordinate-pair labels instead of compass-zone names. These coordinates are generated demo values and are not verified GPS measurements.
