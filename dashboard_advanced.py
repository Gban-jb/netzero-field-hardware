"""Modern, unified Student 4 Streamlit dashboard for Wi-Fi RSSI & SDR readiness."""
from pathlib import Path
import pandas as pd
import io
import zipfile
from datetime import date, datetime, timezone
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from rf_core import (ROOT, DEFAULT_CSV, FREQUENCY_GHZ, FREQUENCY_HZ, CHANNEL,
                     PANEL_COUNT, STRING_COUNT, INVERTER_COUNT, PV_KW_DC,
                     load_csv, summarize, zones_summary, comparison, simulate_rows, write_rows, temperature_flags, filter_day)
from coverage_map import create_map
from panel_overlay import panel_figure, valid_positions, load_panel_catalog, attach_panel_labels
from reports import generate

TEAL='#16836B'; RED='#C2414B'; BLUE='#2563B8'; GRAY='#64748B'

def setup():
    st.set_page_config(page_title='AAMU Student 4 | RF Monitoring',page_icon='📡',layout='wide',initial_sidebar_state='expanded')
    st.markdown('''<style>
    /* AAMU-inspired blue and white interface: clean, restrained and readable. */
    :root {
      --aamu-navy: #12365B;
      --aamu-blue: #1F65A6;
      --aamu-blue-dark: #174E83;
      --aamu-pale: #EAF2FB;
      --aamu-bg: #F4F7FB;
      --aamu-text: #18324F;
      --aamu-muted: #60748B;
      --aamu-border: #D8E2EE;
    }
    .stApp, [data-testid="stAppViewContainer"] {background: var(--aamu-bg); color: var(--aamu-text);}
    [data-testid="stHeader"] {background: rgba(244,247,251,.96); border-bottom: 1px solid var(--aamu-border);}
    .block-container {padding-top: 1.35rem; padding-bottom: 3rem; max-width: 1500px;}
    h1, h2, h3, h4 {color: var(--aamu-navy); letter-spacing: -.02em;}
    p, li, label, .stMarkdown {color: var(--aamu-text);}
    [data-testid="stCaptionContainer"] p {color: var(--aamu-muted);}

    /* Main content surfaces */
    div[data-testid="stMetric"] {
      background: #FFFFFF; padding: 17px 18px; border: 1px solid var(--aamu-border);
      border-left: 4px solid var(--aamu-blue); border-radius: 9px;
      box-shadow: 0 2px 8px rgba(18,54,91,.045);
    }
    div[data-testid="stMetricLabel"] {color: #526A84; font-weight: 600;}
    div[data-testid="stMetricValue"] {color: var(--aamu-navy); font-weight: 750;}
    [data-testid="stVerticalBlockBorderWrapper"] {border-color: var(--aamu-border);}
    hr {border-color: var(--aamu-border);}

    /* University-style identity header */
    .hero {
      border: 1px solid var(--aamu-border); border-left: 6px solid var(--aamu-blue);
      border-radius: 9px; padding: 22px 25px; background: #FFFFFF;
      margin-bottom: 18px; box-shadow: 0 2px 9px rgba(18,54,91,.04);
    }
    .eyebrow {font-size: .72rem; letter-spacing: 2px; font-weight: 800; color: var(--aamu-blue);}
    .hero-title {font-size: 1.95rem; line-height: 1.2; font-weight: 800; color: var(--aamu-navy); margin: 5px 0 6px;}
    .hero-sub {font-size: .96rem; color: var(--aamu-muted);}
    .pill {display: inline-block; background: var(--aamu-pale); color: var(--aamu-blue-dark);
      border: 1px solid #C9DCEF; border-radius: 5px; padding: 5px 10px;
      font-weight: 750; font-size: 11px; letter-spacing: .4px;}

    /* Navigation and controls */
    div[data-testid="stTabs"] button {font-size: .94rem; font-weight: 650; color: #526A84;}
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {gap: 6px; border-bottom: 1px solid var(--aamu-border);}
    div[data-testid="stTabs"] button[aria-selected="true"] {color: var(--aamu-blue-dark);}
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {background: var(--aamu-blue); height: 3px;}
    .stButton > button, .stDownloadButton > button {
      border-radius: 7px; border: 1px solid var(--aamu-blue); background: var(--aamu-blue);
      color: #FFFFFF; font-weight: 650; min-height: 2.45rem;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
      border-color: var(--aamu-blue-dark); background: var(--aamu-blue-dark); color: #FFFFFF;
    }
    [data-baseweb="input"] > div, [data-baseweb="select"] > div,
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea {
      background: #FFFFFF; color: var(--aamu-text); border-color: var(--aamu-border);
      border-radius: 7px;
    }

    /* Deep-blue sidebar with white navigation text */
    [data-testid="stSidebar"] {background: var(--aamu-navy); border-right: 1px solid #0D2B49;}
    [data-testid="stSidebar"] * {color: #F4F8FD;}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color: #C5D5E7;}
    [data-testid="stSidebar"] hr {border-color: rgba(255,255,255,.18);}
    [data-testid="stSidebar"] [data-baseweb="input"] input,
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] [data-testid="stNumberInput"] input {
      background: #FFFFFF !important; color: #18324F !important;
    }
    [data-testid="stSidebar"] .stButton > button {
      background: #FFFFFF; color: var(--aamu-navy); border: 1px solid #D5E2F0;
    }
    [data-testid="stSidebar"] .stButton > button:hover {background: #EAF2FB; color: var(--aamu-blue-dark);}
    [data-testid="stSidebar"] [data-testid="stAlert"] {background: rgba(255,255,255,.10);}

    [data-testid="stDataFrame"] {border: 1px solid var(--aamu-border); border-radius: 8px;}
    </style>''',unsafe_allow_html=True)

def fetch(path):
    try: return load_csv(path)
    except (FileNotFoundError, ValueError, OSError, pd.errors.ParserError) as e:
        st.error(f'Cannot load CSV: {e}');return pd.DataFrame()

def plot_config(fig,height=360):
    fig.update_layout(template='plotly_white',paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',font_color='#18324F',colorway=['#1F65A6','#0F766E','#D97706','#7C3AED','#C2414B'],margin=dict(l=18,r=12,t=26,b=18),height=height,legend_title_text='')
    fig.update_xaxes(gridcolor='#E7EDF5',zerolinecolor='#CBD7E5')
    fig.update_yaxes(gridcolor='#E7EDF5',zerolinecolor='#CBD7E5')
    return fig

@st.fragment(run_every="2s")
def live_simulation_panel(csv_path, weak_threshold, high_threshold, hot_threshold):
    """Software-only live sampler; never controls HackRF or a real receiver."""
    if 'demo_running' not in st.session_state:
        st.session_state.demo_running = False
    if 'demo_connected' not in st.session_state:
        st.session_state.demo_connected = True
    if 'demo_index' not in st.session_state:
        st.session_state.demo_index = 0
    if 'demo_session' not in st.session_state:
        st.session_state.demo_session = 'Live Demo'

    st.subheader('Live simulation controls')
    st.caption('Software-only 2-second simulated RF readings. These buttons do not operate the drone, HackRF or physical transmitter/receiver.')
    session = st.text_input('Simulation session name', value=st.session_state.demo_session, key='demo_name_input')
    a,b,c,d = st.columns(4)
    if a.button('▶ Start Simulation', use_container_width=True):
        if not session.strip():
            st.error('Enter a simulation session name.')
        else:
            st.session_state.demo_session = session.strip()
            st.session_state.demo_running = True
    if b.button('■ Stop Simulation', use_container_width=True):
        st.session_state.demo_running = False
    if c.button('⚠ Simulate Unplug', use_container_width=True):
        st.session_state.demo_connected = False
    if d.button('↻ Reconnect', use_container_width=True):
        st.session_state.demo_connected = True

    running = st.session_state.demo_running
    connected = st.session_state.demo_connected
    status = 'RUNNING' if running and connected else 'PAUSED — MOCK DISCONNECTED' if running else 'STOPPED'
    st.write(f'**Simulation status:** {status}  |  **Mock receiver:** {"CONNECTED" if connected else "DISCONNECTED"}')
    if running and not connected:
        st.warning('Mock receiver unplugged. No simulated samples are recorded until you reconnect.')
    if running and connected:
        try:
            idx = st.session_state.demo_index
            # Keep a consistent 120-point looped route, with varying signal values on repeats.
            rows = simulate_rows(120, seed=55 + idx // 120, survey_id=st.session_state.demo_session)
            row = rows[idx % 120]
            row['timestamp_utc'] = datetime.now(timezone.utc).isoformat()
            write_rows([row], csv_path, append=True)
            st.session_state.demo_index = idx + 1
        except (OSError, ValueError) as exc:
            st.session_state.demo_running = False
            st.error(f'Simulation stopped because saving the CSV failed: {exc}')
    current = fetch(csv_path)
    if not current.empty:
        live = current[current.survey_id.astype(str) == st.session_state.demo_session].tail(60).copy()
        m1,m2,m3 = st.columns(3)
        m1.metric('Session samples', len(current[current.survey_id.astype(str) == st.session_state.demo_session]))
        m2.metric('Latest RSSI', f"{live.value.iloc[-1]:.1f} dBm" if not live.empty else '—')
        m3.metric('Frequency', '5.180 GHz')
        if not live.empty:
            live['sample_number'] = range(1,len(live)+1)
            st.line_chart(live, x='sample_number', y='value', x_label='Recent simulated samples', y_label='RSSI (dBm)')
            flags = temperature_flags(live, hot_threshold, weak_threshold, high_threshold)
            st.caption(f"Recent readings: {int(flags.weak_rf_flag.sum())} weak RSSI flags · {int(flags.high_rssi_flag.sum())} high RSSI flags · {int(flags.high_temperature_flag.sum())} high-temperature flags")
    st.caption('The live panel refreshes automatically. Click Reload CSV to refresh the coverage map, history and all other dashboard tabs.')

def main():
    setup()
    st.sidebar.markdown('## AAMU | RF LAB')
    st.sidebar.caption('STUDENT 4  /  DR. YAQUB PROJECT')
    st.sidebar.caption('Panel project site: 4900 Meridian St N, Huntsville, AL 35811')
    st.sidebar.divider()
    st.sidebar.markdown('**Data source**')
    path_text=st.sidebar.text_input('CSV file',value=str(DEFAULT_CSV),help='Path to a measurements CSV with timestamp, latitude, longitude, value and source')
    path=Path(path_text).expanduser()
    if not path.is_absolute():path=ROOT/path
    threshold=st.sidebar.slider('Weak RSSI threshold (dBm)',-95,-45,-75,1)
    high_rssi_threshold=st.sidebar.slider('High RSSI threshold (dBm)',-70,-20,-45,1,help='Flags unusually strong received Wi-Fi RSSI, not a confirmed fault.')
    if high_rssi_threshold <= threshold:
        st.sidebar.warning('High RSSI threshold must be greater than weak RSSI threshold.')
    min_samples=st.sidebar.slider('Min. samples for zone alerts',2,30,5)
    temp_threshold=st.sidebar.slider('High temperature threshold (°C)',20,65,35,1)
    st.sidebar.caption('Temperature threshold flags paired RF observations for review; it does not prove RF problems are caused by heat.')
    st.sidebar.caption('Weak when RSSI is below your selected threshold; demo threshold is not calibrated.')
    if st.sidebar.button('↻ Reload CSV',use_container_width=True):st.rerun()
    st.sidebar.divider()
    st.sidebar.markdown('**Sample data controls**')
    count=st.sidebar.number_input('Demo samples per survey',min_value=30,max_value=1200,value=120,step=30)
    c1,c2=st.sidebar.columns(2)
    if c1.button('Demo A',use_container_width=True):
        write_rows(simulate_rows(int(count),42,'Demo A'),ROOT/'data'/'measurements.csv',append=False);st.rerun()
    if c2.button('Add B',use_container_width=True):
        write_rows(simulate_rows(int(count),99,'Demo B'),ROOT/'data'/'measurements.csv',append=True);st.rerun()
    st.sidebar.caption('Buttons generate synthetic samples only; they never connect to hardware. They write data/measurements.csv.')
    st.sidebar.caption('Use Start/Stop Simulation in the main dashboard for live mock logging.')
    st.sidebar.divider()
    st.sidebar.info('**Hardware:** Not connected. HackRF spectrum capture + GPS drivers need physical integration and calibration.')

    st.markdown('''<div class="hero"><div class="eyebrow">ALABAMA A&amp;M UNIVERSITY &nbsp; | &nbsp; SOLAR PROJECT</div>
      <div class="hero-title">RF &amp; Communication Monitoring</div>
      <div class="hero-sub">Student 4 · Signal measurements, panel-layout coverage and survey analysis</div>
      <div style="margin-top:12px"><span class="pill">SIMULATION MODE &nbsp;·&nbsp; HARDWARE NOT CONNECTED</span></div></div>''',unsafe_allow_html=True)
    live_simulation_panel(path, threshold, high_rssi_threshold, temp_threshold)
    st.divider()
    df=fetch(path)
    if df.empty:
        st.warning('No valid samples. Use Demo A in the sidebar or run: python rf_survey.py --samples 120')
        return
    surveys=sorted(df.survey_id.dropna().astype(str).unique().tolist())
    select=st.multiselect('Survey sessions',surveys,default=surveys)
    shown=df[df.survey_id.astype(str).isin(select)].copy()
    # Use the same simulated latitude/longitude labels throughout the dashboard.
    shown['latitude']=pd.to_numeric(shown['latitude'],errors='coerce')
    shown['longitude']=pd.to_numeric(shown['longitude'],errors='coerce')
    shown['zone_id']=shown.apply(lambda r: f"({r.latitude:.6f}, {r.longitude:.6f})" if pd.notna(r.latitude) and pd.notna(r.longitude) else 'Coordinates unavailable',axis=1)
    shown=temperature_flags(shown,temp_threshold,threshold,high_rssi_threshold)
    shown=attach_panel_labels(shown)
    if shown.empty:st.info('Choose at least one survey.');return
    stats=summarize(shown,threshold)
    demo=shown.source.astype(str).str.upper().eq('SIMULATED').any()
    if demo:st.warning('**SIMULATED DATA:** Signal values, routes and longitude are fabricated for demonstration. No real measurements or surveyed panel GPS positions are claimed.')
    a,b,c,d,e=st.columns(5)
    a.metric('Recorded samples',f"{stats['samples']:,}")
    b.metric('Average RSSI',f"{stats['avg']:.1f} dBm")
    c.metric('Weak readings',f"{stats['weak']:,}",f"{stats['weak_pct']}% of samples",delta_color='off')
    d.metric('Target frequency',f'{FREQUENCY_GHZ:.3f} GHz')
    e.metric('High RSSI flags',int(shown.high_rssi_flag.sum()))
    st.caption(f'Weak RF: below {threshold} dBm · High RF: above {high_rssi_threshold} dBm · Values equal to a threshold are not flagged. Strong RSSI is not necessarily a problem.')

    tab1,tab2,tab3,tab4,tab5,tab6=st.tabs(['▦ Overview','◉ Panel coverage + heatmap','⌁ Signals & trends','▤ Survey comparison','📅 Daily history','⚙ Hardware & exports'])
    with tab1:
        left,right=st.columns([1.35,1],gap='large')
        with left:
            st.subheader('Solar installation reference')
            st.image(str(ROOT/'assets'/'site_plan_page4.png'),caption='Final site-layout drawing supplied for project planning • Sheet WI101, page 4. Do not infer precise WGS84 coordinates from this image.',use_container_width=True)
        with right:
            st.subheader('Site at a glance')
            st.markdown('**Project location:** 4900 Meridian Street North, Huntsville, AL 35811, USA')
            st.caption('Location identified in the engineering PDF cover sheet GI001. Exact GPS coordinates of individual panel rows are not confirmed.')
            x1,x2=st.columns(2)
            x1.metric('Solar modules',f'{PANEL_COUNT:,}')
            x2.metric('PV strings',STRING_COUNT)
            x3,x4=st.columns(2)
            x3.metric('Panels / string',27)
            x4.metric('Inverters',INVERTER_COUNT)
            st.metric('DC system rating',f'{PV_KW_DC:,.2f} kW')
            st.caption('JA Solar JAM72D30 545/MB modules • fixed ground mount • 20° tilt • 180° azimuth. Values are from the provided engineering drawing.')
            st.info('The Excel management diagram identifies **2,538 T/B module positions across rows A–P**. The panel ID catalog is mapped to approximate *drawing pixel positions*, **not** surveyed GPS. RF coordinates and sample-to-panel matches remain synthetic.')
        st.subheader('Field setup: transmitter and receiver')
        st.info('**Proposed geometry:** transmitter on one side of the panel rows and receiver on the opposite side. Record their actual positions, antenna heights, orientation, and line-of-sight when hardware arrives. The WEST → EAST illustration in synthetic data is only a schematic, not a verified site placement.')
        st.markdown('**Transmitter (side A) → Solar panel rows → Receiver (side B)**')
        st.caption('The drone may photograph the setup from above with RGB and thermal cameras, but the photos must be synchronized by time/location and labeled manually until flight integration is available.')
        st.subheader('Weak-coverage zones')
        z=zones_summary(shown,threshold,min_samples)
        if not z.empty:
            fig=px.bar(z,x='zone_id',y='weak_pct',color='alert',color_discrete_map={True:RED,False:TEAL},hover_data=['samples','avg_dbm','weak_count'],labels={'zone_id':'GPS coordinates (simulated)','weak_pct':'Weak samples (%)','alert':'Zone alert'})
            fig.update_yaxes(range=[0,100]);st.plotly_chart(plot_config(fig,330),use_container_width=True)
            st.dataframe(z,use_container_width=True,hide_index=True)
            st.caption('Each label is a simulated latitude/longitude pair. Alert rule: ≥40% weak readings with at least minimum sample count.')
    with tab2:
        st.subheader('RF coverage on the solar panel drawing')
        st.caption('The actual panel layout from engineering sheet WI101 is used as the background — not a street/GPS map. '
                   'The marker positions are *schematic demo positions*, not surveyed readings at the illustrated panel rows.')
        eligible=valid_positions(shown)
        if eligible.empty:
            st.warning('This CSV has no valid layout_x and layout_y values. The panel image cannot be aligned from GPS alone. '
                       'Record verified panel/image coordinates before plotting real measurements.')
        else:
            if len(eligible)<len(shown):
                st.warning(f'{len(shown)-len(eligible)} readings have no valid panel-layout coordinates, so they are not plotted.')
            catalog=load_panel_catalog()
            st.markdown('#### Excel panel identification')
            cfind,clabel=st.columns([2.2,1.2])
            selected_id=cfind.selectbox(
                'Find and highlight a named panel (A–P; T = top / B = bottom)',
                ['No selection']+catalog.panel_id.tolist(),
                help='IDs are generated from the row letter, numbered cell and T/B markers in the supplied Excel sheet.')
            show_names=clabel.checkbox('Display names beside RF points',value=True)
            st.caption('The catalog contains all 2,538 labelled module positions. Hover over a panel on the drawing '
                       'to inspect its individual Excel ID, or select an ID above to highlight it. '
                       'Each simulated RF measurement is assigned the closest *numbered panel pair*; '
                       'it cannot distinguish a top module from a bottom module.')
            highlight_id=None if selected_id=='No selection' else selected_id
            if highlight_id:
                selected_row=catalog.loc[catalog.panel_id.eq(highlight_id)].iloc[0]
                st.info(f'**{highlight_id}** · Excel sheet SOLAR FARM, cell '
                        f'**{selected_row.excel_number_cell}** · Row **{selected_row.row_id}** · '
                        f'Drawing pixel ({selected_row.panel_px_x:.1f}, {selected_row.panel_px_y:.1f}). '
                        'No verified individual-panel latitude/longitude is provided.')
            a_tab,b_tab=st.tabs(['● Coverage points','🌡 Signal strength heat map'])
            with a_tab:
                st.markdown('**Coverage markers:** 🔴 weak RSSI · 🟣 weak + hot · 🟠 hot only · 🔵 high RSSI · 🟢 normal RSSI.')
                fig,n=panel_figure(eligible,weak=threshold,high=high_rssi_threshold,temperature=temp_threshold,
                                   view='coverage',show_labels=show_names,highlight_panel=highlight_id)
                if fig is not None:
                    event=st.plotly_chart(fig,use_container_width=True,key='solar_panel_coverage',on_select='rerun',selection_mode='points')
                    selected_points=getattr(getattr(event,'selection',None),'points',[]) if event is not None else []
                    if selected_points:
                        chosen_point=selected_points[0]
                        coords=chosen_point.get('customdata') if isinstance(chosen_point,dict) else None
                        if coords is not None and len(coords)>=4:
                            st.success(f"Closest Excel pair: {coords[2]} / {coords[3]} · "
                                       f"Synthetic latitude {float(coords[0]):.6f}, "
                                       f"longitude {float(coords[1]):.6f}. "
                                       "Neither module's surveyed GPS position is known.")
                    st.caption(f'{n} plotted demo samples. Hover for Excel module pair names, RSSI, and synthetic latitude/longitude. You can zoom into rows to inspect individual catalog IDs. Empty areas are not evidence of good coverage.')
                    html_file=create_map(path,ROOT/'outputs'/'coverage_map.html',threshold,temp_threshold,high_rssi_threshold,'coverage')
                    st.download_button('↓ Download interactive panel coverage HTML',data=html_file.read_bytes(),
                                       file_name='panel_coverage.html',mime='text/html')
            with b_tab:
                st.caption('Heat map colors: 🔴 weak (more negative dBm) → 🟡 moderate → 🟢 strong (less negative dBm). '
                           'The estimated colors only cover drawn panel rows close to demo samples; uncovered areas stay visible.')
                show_heat_dots=st.checkbox('Show sampled locations on the heat map',value=False)
                fig,n=panel_figure(eligible,weak=threshold,high=high_rssi_threshold,temperature=temp_threshold,
                                   view='heatmap',points_on_heat=show_heat_dots,
                                   show_labels=show_names,highlight_panel=highlight_id)
                if fig is not None:
                    st.plotly_chart(fig,use_container_width=True,key='solar_panel_heatmap')
                    st.caption('This heat map interpolates synthetic readings. It is a visualization, NOT verified RF coverage or evidence of a physical problem.')
                    html_file=create_map(path,ROOT/'outputs'/'panel_heatmap.html',threshold,temp_threshold,high_rssi_threshold,'heatmap')
                    st.download_button('↓ Download interactive panel heat map HTML',data=html_file.read_bytes(),
                                       file_name='panel_heatmap.html',mime='text/html')
        with st.expander('Synthetic RF readings matched to Excel panel pairs',expanded=False):
            columns=['timestamp_utc','survey_id','panel_pair_label','panel_id_top',
                     'panel_id_bottom','latitude','longitude','value','units']
            st.dataframe(shown[columns],use_container_width=True,hide_index=True)
            st.download_button('↓ Download readings with nearby Excel panel IDs',
                               shown.to_csv(index=False).encode('utf-8'),
                               file_name='RF_simulated_readings_with_Excel_panel_IDs.csv',
                               mime='text/csv',key='panel_labeled_export')
            st.caption('The coordinates are synthetic and the nearby Excel ID is a schematic match, not a measured panel location.')
        st.info('**Future real measurements:** Use calibrated GPS + surveyed alignment or record validated image positions '
                'for each measurement. Neither the original layout nor the demo coordinates establish real panel locations.')
    with tab3:
        l,r=st.columns([1.5,1],gap='large')
        with l:
            st.subheader('RSSI over samples')
            plot=shown.reset_index(drop=True).copy();plot['sample']=plot.index+1
            fig=px.line(plot,x='sample',y='value',color='survey_id',markers=True,hover_data=['panel_pair_label','latitude','longitude'],labels={'value':'RSSI (dBm)','sample':'Sample index','survey_id':'Survey','panel_pair_label':'Nearby Excel panel pair','latitude':'Synthetic latitude','longitude':'Synthetic longitude'})
            fig.add_hline(y=threshold,line_dash='dash',line_color=RED,annotation_text=f'Weak threshold {threshold} dBm')
            fig.add_hline(y=high_rssi_threshold,line_dash='dot',line_color=BLUE,annotation_text=f'High RSSI {high_rssi_threshold} dBm')
            st.plotly_chart(plot_config(fig,410),use_container_width=True)
        with r:
            st.subheader('Signal distribution')
            fig=px.histogram(shown,x='value',nbins=22,color='survey_id',labels={'value':'RSSI (dBm)'},barmode='overlay',opacity=.75)
            fig.add_vline(x=threshold,line_dash='dash',line_color=RED)
            fig.add_vline(x=high_rssi_threshold,line_dash='dot',line_color=BLUE)
            st.plotly_chart(plot_config(fig,410),use_container_width=True)
        st.subheader('Threshold flags')
        st.metric('RSSI values exceeding high threshold',int(shown.high_rssi_flag.sum()))
        st.caption('High RSSI flags are strong received signals. They are not proof of harmful interference.')
        st.subheader('Temperature-linked RF review')
        st.metric('RF readings taken above temperature threshold',int(shown.high_temperature_flag.sum()))
        st.metric('Weak RF readings also above temperature threshold',int(shown.combined_review_flag.sum()))
        tdf=shown.dropna(subset=['temperature_c']).copy()
        if not tdf.empty:
            tfig=px.scatter(tdf,x='temperature_c',y='value',color='status' if 'status' in tdf.columns else 'survey_id',hover_data=['timestamp_utc','latitude','longitude','panel_pair_label'],labels={'temperature_c':'Temperature (°C)','value':'Wi-Fi RSSI (dBm)','panel_pair_label':'Nearby Excel panel pair'})
            tfig.add_vline(x=temp_threshold,line_dash='dash',line_color='#F59E0B')
            tfig.add_hline(y=threshold,line_dash='dash',line_color=RED)
            tfig.add_hline(y=high_rssi_threshold,line_dash='dot',line_color=BLUE)
            st.plotly_chart(plot_config(tfig,340),use_container_width=True)
        else: st.info('No temperature readings in this CSV. Add real temperature_c data to enable flags.')
        st.caption('A hot reading is a review flag, not evidence temperature caused weaker RF. Match temperature and RF observations from the same time/location; demo temperatures are simulated.')
        st.subheader('Frequency and receiver details')
        a,b,c=st.columns(3)
        a.metric('Target center frequency',f'{FREQUENCY_HZ:,} Hz')
        b.metric('Wi-Fi channel',f'{CHANNEL}')
        c.metric('Imported data sources',', '.join(sorted(shown.source.astype(str).unique()))[:45])
        st.info('**5.180 GHz is a frequency, not an RSSI value.** HackRF signal power is not automatically Wi-Fi RSSI: calibration, correct hardware settings, and separate units are required.')
    with tab4:
        st.subheader('Compare two survey sessions')
        if len(surveys)<2:
            st.info('Add Demo B using the sidebar to enable a two-session comparison.')
        else:
            s1,s2=st.columns(2)
            baseline=s1.selectbox('Baseline session',surveys,index=0)
            followup=s2.selectbox('Follow-up session',surveys,index=1)
            if baseline==followup: st.warning('Choose different sessions.')
            else:
                grouped=comparison(df[df.survey_id.astype(str).isin([baseline,followup])])
                pivot=grouped.pivot(index='zone_id',columns='survey_id',values='avg_dbm')
                if baseline in pivot and followup in pivot:
                    pivot['change_db']=pivot[followup]-pivot[baseline]
                    st.dataframe(pivot.reset_index().round(1),use_container_width=True,hide_index=True)
                    st.caption('Change is follow-up minus baseline; positive means stronger average RSSI. This is a **zone-average** comparison, not GPS-nearest-neighbor matching.')
                    fig=px.bar(pivot.reset_index(),x='zone_id',y='change_db',color='change_db',color_continuous_scale='RdYlGn',labels={'change_db':'Change in mean RSSI (dB)','zone_id':'GPS coordinates (simulated)'})
                    fig.add_hline(y=0,line_color=GRAY);st.plotly_chart(plot_config(fig,350),use_container_width=True)
    with tab5:
        st.subheader('Daily history and downloadable record')
        st.caption('Select a UTC date from stored measurement records. The saved CSV is the history source; maintain backups and do not overwrite actual survey records with Demo A.')
        dt=pd.to_datetime(df.timestamp_utc,utc=True,errors='coerce')
        available=sorted({d for d in dt.dt.date.dropna()})
        if available:
            chosen=st.selectbox('Recorded day (UTC)',available,index=len(available)-1,format_func=lambda d:d.isoformat())
            daily=attach_panel_labels(filter_day(df,chosen))
            st.metric('Readings on selected day',len(daily))
            st.dataframe(daily,use_container_width=True,hide_index=True)
            st.download_button('↓ Download this day as CSV',daily.to_csv(index=False).encode('utf-8'),file_name=f'RF_history_{chosen}.csv',mime='text/csv',use_container_width=True)
        else: st.info('There are no valid timestamps in the CSV.')
        st.divider()
        st.subheader('Drone RGB / thermal photo evidence')
        st.caption('Upload drone images captured over the transmitter-panel-receiver setup. Images are included in an evidence ZIP for this session, alongside the selected day’s CSV; no automatic geolocation, image interpretation, or image retention is claimed.')
        photos=st.file_uploader('Add RGB or thermal snapshots',type=['jpg','jpeg','png','tif','tiff'],accept_multiple_files=True)
        notes=st.text_area('Photo notes (time, drone position, image type, observed conditions)',placeholder='Example: RGB overhead image at 15:20 UTC, transmitter left of panels, receiver right...')
        if photos and available:
            buff=io.BytesIO()
            with zipfile.ZipFile(buff,'w',zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(f'measurements_{chosen}.csv',daily.to_csv(index=False))
                archive.writestr('PHOTO_NOTES.txt',notes or 'No photo notes entered. Capture times and locations must be verified.')
                for j,pic in enumerate(photos):
                    archive.writestr(f'drone_images/{j+1:02d}_{Path(pic.name).name}',pic.getvalue())
            st.download_button('↓ Download day + drone photos ZIP',buff.getvalue(),file_name=f'AAMU_RF_Drone_Evidence_{chosen}.zip',mime='application/zip',use_container_width=True)
        st.warning('Demo records use synthetic dates and locations. A true historical record requires actual dated measurements and photos to be saved over time.')
    with tab6:
        l,r=st.columns(2,gap='large')
        with l:
            st.subheader('Kit status')
            st.error('Physical measurement kit: **NOT CONNECTED**')
            st.write('**Planned receiver:** laptop/Raspberry Pi with GPS + permitted Wi-Fi adapter OR receive-only HackRF SDR')
            st.write('**GPS state:** only the last CSV field is shown; no live GPS communication is occurring.')
            st.write('**Start / Stop:** live mock simulation and simulated unplug/reconnect controls appear above the overview. Physical hardware controls are not implemented.')
            st.write('**HackRF path:** `hardware_adapter.py` contains marked integration points; actual hardware drivers, calibrated units and GPS synchronization are pending.')
            st.caption('No RF capture/transmission is performed by this dashboard.')
        with r:
            st.subheader('Export & handover')
            st.download_button('↓ Download filtered data CSV (includes Excel panel labels)',
                               shown.to_csv(index=False).encode(),
                               file_name='student4_filtered_measurements_with_panel_IDs.csv',
                               mime='text/csv',use_container_width=True)
            st.download_button('↓ Download all 2,538 panel IDs and drawing coordinates',
                               (ROOT/'data'/'panel_catalog.csv').read_bytes(),
                               file_name='panel_catalog_Excel_drawing_positions.csv',
                               mime='text/csv',use_container_width=True)
            if st.button('Prepare reports',use_container_width=True):
                report=generate(path,threshold=threshold,minimum=min_samples)
                st.success('Summary JSON and zone CSV saved in outputs/.')
            for fn,mime in [('summary_report.json','application/json'),('zone_report.csv','text/csv')]:
                p=ROOT/'outputs'/fn
                if p.exists():st.download_button(f'↓ {fn}',p.read_bytes(),file_name=fn,mime=mime,use_container_width=True)
            st.info('See README.md, docs/PANEL_ID_MAPPING.md and docs/HARDWARE_INTEGRATION.md for how panel IDs were extracted from Excel, the important simulated-data limitations and setup instructions.')
    st.divider()
    st.caption('AAMU Student 4 · Passive, permission-based RF survey prototype · Layout provided by project team · Weak RSSI is not proof of RF interference')

if __name__=='__main__':main()
