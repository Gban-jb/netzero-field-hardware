"""Entry point for Streamlit Community Cloud.

Streamlit Cloud looks for `streamlit_app.py` at the repository root by
default. The dashboard itself lives in `dashboard.py`; this file only
calls it, so the app deploys without anyone having to set a custom main
file path.

Running `streamlit run dashboard.py` locally still works exactly as before.
"""

from dashboard import main

main()
