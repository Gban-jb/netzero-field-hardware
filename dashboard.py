"""Fall-only Student 4 RF/GPS prototype dashboard.

This edition shows the five Fall requirements only. Synthetic measurements are
never represented as physical RF/GPS sensor data. The original full dashboard
remains available as dashboard_advanced.py.
"""
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import streamlit as st
from rf_core import ROOT, DEFAULT_CSV, load_csv, write_rows, simulate_rows, summarize
from panel_overlay import attach_panel_labels, load_panel_catalog, valid_positions, panel_figure
from coverage_map import create_map
from reports import generate
from dashboard_advanced import setup, fetch

WEAK_DEFAULT = -75


@st.fragment(run_every="2s")
def mock_live_logger(csv_path: Path):
    """A mock receiver for demonstrating a working start/stop/unplug UI.

    It does not poll any GPS, SDR or Wi-Fi interface. The simulated logger does
    write a correctly structured, timestamped CSV sample when running.
    """
    state = st.session_state
    state.setdefault('fall_running', False)
    state.setdefault('fall_connected', True)
    state.setdefault('fall_sample_index', 0)
    state.setdefault('fall_session_id', 'Fall Live Simulation')

    st.subheader('Receiver & GPS status')
    st.warning('**DEMO / NO HARDWARE CONNECTION.** GPS coordinates, Wi-Fi RSSI and receiver status below are simulated. Real sensor input is not implemented.')
    session = st.text_input('Demo session name', value=state.fall_session_id, key='fall_session_name_input')
    c1, c2, c3, c4 = st.columns(4)
    if c1.button('▶ Start demo', use_container_width=True):
        if not session.strip():
            st.error('Enter a session name first.')
        else:
            state.fall_session_id = session.strip()
            state.fall_running = True
    if c2.button('■ Stop demo', use_container_width=True):
        state.fall_running = False
    if c3.button('⚠ Mock unplug', use_container_width=True):
        state.fall_connected = False
    if c4.button('↻ Mock reconnect', use_container_width=True):
        state.fall_connected = True

    running, connected = state.fall_running, state.fall_connected
    if running and connected:
        try:
            index = state.fall_sample_index
            row = simulate_rows(120, seed=55 + index // 120, survey_id=state.fall_session_id)[index % 120]
            row['timestamp_utc'] = datetime.now(timezone.utc).isoformat()
            write_rows([row], csv_path, append=True)
            state.fall_sample_index = index + 1
        except (ValueError, OSError) as exc:
            state.fall_running = False
            st.error(f'Could not write the demo CSV: {exc}')
    if running and not connected:
        st.warning('Mock receiver disconnected: simulated logging is paused until reconnect.')

    stt = 'DEMO LOGGING' if running and connected else 'PAUSED (MOCK DISCONNECT)' if running else 'STOPPED'
    x1, x2, x3 = st.columns(3)
    x1.metric('Demo logger state', stt)
    x2.metric('Receiver connection', 'MOCK connected' if connected else 'MOCK disconnected')
    x3.metric('Physical GPS', 'NOT CONNECTED')

    logged = fetch(csv_path)
    session_rows = logged[logged.survey_id.astype(str).eq(state.fall_session_id)] if not logged.empty else logged
    if not session_rows.empty:
        newest = session_rows.iloc[-1]
        st.markdown(f"**Most recent mock sample:** RSSI **{newest.value:.1f} dBm** · "
                    f"Latitude **{newest.latitude:.6f}** · Longitude **{newest.longitude:.6f}**")
        st.caption(f"UTC sample time: {newest.timestamp_utc} · Session records: {len(session_rows)} · "
                   "GPS coordinates and radio measurements are SYNTHETIC")
    else:
        st.info('Start the simulation to append synthetic samples to the CSV.')
    st.caption('The demo automatically writes one sample about every two seconds. Stop before switching CSV files. '
               'Reload the page to update the other tabs from saved records.')


def prepare_data(path: Path, weak_threshold: int):
    df = fetch(path)
    if df.empty:
        return df
    df = attach_panel_labels(df)
    df['weak'] = df.value.lt(weak_threshold)
    return df


def main():
    setup()
    st.sidebar.markdown('## AAMU | FALL RF KIT')
    st.sidebar.caption('STUDENT 4 · DR. YAQUB SOLAR PROJECT')
    st.sidebar.markdown('**Measurement file**')
    csv_input = st.sidebar.text_input('CSV file path', value=str(DEFAULT_CSV),
                                     help='Measurements are read from and mock samples are written to this CSV.')
    path = Path(csv_input).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    weak_threshold = st.sidebar.slider('Weak signal cutoff (dBm)', -95, -45, WEAK_DEFAULT)
    st.sidebar.caption(f'RSSI below {weak_threshold} dBm is displayed as weak; this is a demonstration threshold.')
    if st.sidebar.button('↻ Reload saved CSV', use_container_width=True):
        st.rerun()
    st.sidebar.divider()
    st.sidebar.markdown('**Sample data**')
    count = st.sidebar.number_input('Readings per demo session', 30, 1200, 120, step=30)
    a, b = st.sidebar.columns(2)
    if a.button('Demo A', use_container_width=True):
        if st.session_state.get('fall_running', False):
            st.sidebar.warning('Stop the running demo before replacing the CSV.')
        else:
            write_rows(simulate_rows(int(count), 42, 'Demo A'), path, append=False)
            st.rerun()
    if b.button('Add Demo B', use_container_width=True):
        write_rows(simulate_rows(int(count), 99, 'Demo B'), path, append=True)
        st.rerun()
    st.sidebar.caption('Demo A **replaces** the selected CSV. Back up actual survey data before generating demos.')
    st.sidebar.error('REAL GPS / RF KIT: NOT CONNECTED')
    st.sidebar.caption('A physical receive-only RF/GPS kit and permitted field measurements are needed for real results.')

    st.markdown('''<div class="hero"><div class="eyebrow">ALABAMA A&amp;M UNIVERSITY  |  FALL DEMONSTRATION</div>
    <div class="hero-title">Portable RF / GPS Survey Kit</div>
    <div class="hero-sub">Student 4 · The five required Fall prototype views</div>
    <div style="margin-top:12px"><span class="pill">SIMULATED DATA · NO PHYSICAL SENSOR CONNECTED</span></div></div>''',
    unsafe_allow_html=True)
    df = prepare_data(path, weak_threshold)
    if not df.empty:
        stats = summarize(df, weak_threshold)
        a, b, c = st.columns(3)
        a.metric('Saved CSV readings', f"{stats['samples']:,}")
        b.metric('Mean RSSI', f"{stats['avg']:.1f} dBm")
        c.metric('Weak samples', f"{stats['weak']:,} ({stats['weak_pct']:.1f}%)")
    st.caption('The engineering panel layout and Excel panel IDs are genuine source references; '
               'the supplied RF/GPS survey points and their nearest-panel matches are simulated.')

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        '📍 GPS + RF', '⏺ Live status', '▤ CSV logger', '◉ Coverage + heatmap', '▶ Replay + export'
    ])

    with tab1:
        st.subheader('GPS coordinates & RF signal measurements')
        st.caption('Displays the most recently stored sample. It is not live hardware telemetry.')
        if df.empty:
            st.info('No readings are stored yet. Choose Demo A in the sidebar or start the mock logger on Live status.')
        else:
            newest = df.iloc[-1]
            a, b, c, d = st.columns(4)
            a.metric('Latitude', f'{newest.latitude:.6f}')
            b.metric('Longitude', f'{newest.longitude:.6f}')
            c.metric('RSSI', f'{newest.value:.1f} dBm')
            d.metric('Signal', 'WEAK' if bool(newest.weak) else 'ABOVE CUTOFF')
            st.write(f'**Timestamp (UTC):** {newest.timestamp_utc}')
            st.write(f'**Survey session:** {newest.survey_id} · **Data source:** {newest.source}')
            st.write('**GPS lock:** NOT VERIFIED — sample fields are demo values, not a physical GPS fix')
            st.write('**Receiver:** NOT CONNECTED · **RF measurement type:** Wi-Fi RSSI (simulated dBm)')
            st.warning('These coordinates do not establish the real GPS location of any solar panel.')

    with tab2:
        mock_live_logger(path)

    with tab3:
        st.subheader('Timestamped CSV measurement logger')
        st.markdown('The Python code records each sample with **UTC time, latitude, longitude, RF value, units, survey ID and receiver ID**. '
                    'Use the Live status tab to start/stop mock sampling. The original `rf_survey.py` script can also generate a demo CSV.')
        st.code('python rf_survey.py --mode simulate --samples 30 --output data/measurements.csv', language='bash')
        st.caption(f'Current CSV: {path}')
        if df.empty:
            st.info('No valid CSV records found yet.')
        else:
            fields = [c for c in ['timestamp_utc','latitude','longitude','measurement_type','value','units',
                                   'receiver_id','survey_id','gps_lock','source','hardware_status'] if c in df.columns]
            st.dataframe(df[fields].tail(100).iloc[::-1], use_container_width=True, hide_index=True)
            st.download_button('↓ Download measurement CSV', data=path.read_bytes(),
                               file_name='fall_rf_measurements.csv', mime='text/csv',
                               use_container_width=True, key='fall_logger_csv')
            st.caption('The records shown are from the selected file. Download saves the full raw CSV; '
                       'the table is limited to the most recent 100 readings.')

    with tab4:
        st.subheader('RF coverage and signal-strength heatmap')
        st.caption('Both maps use the same solar-farm drawing and Excel panel IDs. The GPS/RSSI survey readings and '
                   'matches to nearby panels are simulated, and the drawing is not georeferenced.')
        if df.empty:
            st.info('Generate or import readings before plotting coverage and the heatmap.')
        else:
            samples = valid_positions(df)
            if samples.empty:
                st.warning('No drawing-aligned positions are present in this CSV. Real GPS measurements must be '
                           'georeferenced to the panel drawing before they can be plotted here.')
            else:
                catalog = load_panel_catalog()
                left, right = st.columns([2, 1])
                pick = left.selectbox('Find a named solar panel',
                                      ['No selection'] + catalog.panel_id.tolist(),
                                      key='fall_panel_selector')
                show_names = right.checkbox('Label measured points with panel IDs', value=True,
                                            key='fall_panel_labels')
                highlight = None if pick == 'No selection' else pick
                points_tab, heat_tab = st.tabs(['● Coverage points', '🌡 RSSI heatmap'])
                with points_tab:
                    st.markdown('**Red** = weak readings (below the selected threshold). '
                                'Other marker colors indicate measured or simulated signal categories.')
                    fig, n = panel_figure(samples, weak=weak_threshold, view='coverage',
                                          show_labels=show_names, highlight_panel=highlight)
                    if fig is not None:
                        st.plotly_chart(fig, use_container_width=True, key='fall_coverage_points')
                    st.caption(f'{n} schematic RF samples displayed. Red markers are below '
                               f'{weak_threshold} dBm. Pale panel positions and places with no readings are '
                               '**unsampled**, not proof of good coverage. Hover to inspect the nearby Excel T/B pair.')
                    if len(samples) < len(df):
                        st.warning(f'{len(df) - len(samples)} readings without valid drawing positions were not plotted.')
                    try:
                        html_path = create_map(path, ROOT/'outputs'/'coverage_map.html',
                                               weak_threshold, 35, -45, 'coverage')
                        st.download_button('↓ Download coverage points (HTML)',
                                           data=html_path.read_bytes(),
                                           file_name='fall_coverage_points.html', mime='text/html',
                                           use_container_width=True, key='fall_coverage_html')
                    except (OSError, ValueError) as exc:
                        st.error(f'Unable to export coverage map: {exc}')
                with heat_tab:
                    st.markdown('**Heatmap color guide:** 🔴 weaker RF signal → 🟡 moderate → 🟢 stronger RF signal. '
                                'The heatmap only estimates RSSI near sampled parts of the drawing; '
                                'areas without nearby samples are left transparent.')
                    show_heat_dots = st.checkbox('Show measurement dots on the heatmap', value=True,
                                                 key='fall_heatmap_dots')
                    fig, n = panel_figure(samples, weak=weak_threshold, view='heatmap',
                                          points_on_heat=show_heat_dots,
                                          show_labels=show_names, highlight_panel=highlight)
                    if fig is not None:
                        st.plotly_chart(fig, use_container_width=True, key='fall_heatmap_chart')
                    st.caption(f'Heatmap based on {n} simulated RF samples. '
                               f'The weak-signal threshold is {weak_threshold} dBm. '
                               'Interpolated colors are illustrative, not verified RF coverage or '
                               'individual solar-module measurements.')
                    try:
                        heat_path = create_map(path, ROOT/'outputs'/'panel_heatmap.html',
                                               weak_threshold, 35, -45, 'heatmap')
                        st.download_button('↓ Download RSSI heatmap (HTML)',
                                           data=heat_path.read_bytes(),
                                           file_name='fall_signal_heatmap.html', mime='text/html',
                                           use_container_width=True, key='fall_heatmap_html')
                    except (OSError, ValueError) as exc:
                        st.error(f'Unable to export heatmap: {exc}')
                st.info('Excel panel names describe locations on the supplied drawing. Each simulated reading is '
                        'matched to the nearest illustrative top/bottom panel pair, not to a surveyed module GPS point.')

    with tab5:
        st.subheader('Replay a stored survey + export results')
        st.caption('Use the slider or Next button to step through timestamped measurements. '
                   'This replays the saved CSV; it does not trigger new RF measurements.')
        if df.empty:
            st.info('Add at least one demo survey or import a measurement CSV to enable playback.')
        else:
            sessions = sorted(df.survey_id.dropna().astype(str).unique())
            selected_session = st.selectbox('Saved survey', sessions)
            route = df[df.survey_id.astype(str).eq(selected_session)].sort_values('timestamp_utc').reset_index(drop=True)
            if st.session_state.get('fall_replay_session') != selected_session:
                st.session_state.fall_replay_session = selected_session
                st.session_state.fall_replay_position = 1
            if st.session_state.get('fall_replay_position', 1) > len(route):
                st.session_state.fall_replay_position = len(route)
            x, y, z = st.columns([1, 1, 2])
            if x.button('↤ First sample', use_container_width=True):
                st.session_state.fall_replay_position = 1
            if y.button('Next sample →', use_container_width=True):
                st.session_state.fall_replay_position = min(len(route), st.session_state.fall_replay_position + 1)
            st.slider('Replay progress (sample number)', min_value=1, max_value=len(route),
                      key='fall_replay_position')
            position = st.session_state.fall_replay_position
            current = route.iloc[position-1]
            z.metric('Replay position', f'{position} / {len(route)}')
            st.write(f'**Sample time (UTC):** {current.timestamp_utc} · '
                     f'**RSSI:** {current.value:.1f} dBm · '
                     f'**Simulated GPS:** {current.latitude:.6f}, {current.longitude:.6f}')
            accumulated = valid_positions(route.iloc[:position].copy())
            if not accumulated.empty:
                fig, plotted = panel_figure(accumulated, weak=weak_threshold, show_labels=False)
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption(f'Showing {plotted} stored, schematic drawing points through sample {position}; '
                               'unmarked areas are not measured. Each point uses the saved synthetic data.')
            else:
                st.info('This survey does not contain the schematic drawing coordinates needed for image replay.')
            st.divider()
            st.subheader('Save your outputs')
            c1, c2 = st.columns(2)
            c1.download_button('↓ Export selected survey CSV',
                               route.to_csv(index=False).encode('utf-8'),
                               file_name=f'fall_survey_{selected_session.replace(" ", "_")}.csv',
                               mime='text/csv', use_container_width=True)
            c2.download_button('↓ Export all readings CSV', path.read_bytes(),
                               file_name='fall_all_measurements.csv', mime='text/csv', use_container_width=True)
            if st.button('Prepare summary report', use_container_width=True):
                try:
                    generate(path, threshold=weak_threshold, minimum=5)
                    st.success('Summary JSON and zone CSV saved in outputs/.')
                except (ValueError, OSError) as exc:
                    st.error(f'Failed to prepare report: {exc}')
            for name, mime in [('summary_report.json', 'application/json'), ('zone_report.csv', 'text/csv')]:
                file = ROOT/'outputs'/name
                if file.exists():
                    st.download_button(f'↓ {name}', data=file.read_bytes(), file_name=name,
                                       mime=mime, use_container_width=True)
    st.divider()
    st.caption('Student 4 · Fall prototype only · Simulated RF/GPS data and Excel panel-name overlay '
               '· Ground-based receiver proof-of-concept (physical hardware still pending)')


if __name__ == '__main__':
    main()
