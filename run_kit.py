"""Cross-platform entry point. Uses current Python interpreter and installed dependencies."""
import subprocess
import sys
from pathlib import Path
from rf_core import ROOT, DEFAULT_CSV

def main():
    if not DEFAULT_CSV.exists():
        subprocess.run([sys.executable,str(ROOT/'rf_survey.py'),'--samples','120'],check=True)
    subprocess.run([sys.executable,str(ROOT/'coverage_map.py')],check=True)
    subprocess.run([sys.executable,str(ROOT/'coverage_map.py'),'--view','heatmap'],check=True)
    subprocess.run([sys.executable,str(ROOT/'reports.py')],check=True)
    try:
        subprocess.run([sys.executable,'-m','streamlit','run',str(ROOT/'dashboard.py'),'--server.address=127.0.0.1','--server.port=8501','--browser.gatherUsageStats=false'],check=True)
    except KeyboardInterrupt:
        print('Stopped Streamlit dashboard.')
if __name__=='__main__':main()
