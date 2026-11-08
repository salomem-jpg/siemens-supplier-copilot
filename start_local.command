#!/bin/bash
set -e
cd "$(dirname "$0")"
echo 'Starting Siemens Supplier Capability Studio (synthetic demo)...'
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
