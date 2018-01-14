#!/bin/bash
source .venv/bin/activate
pip install --upgrade .
rhoci-server --debug -p 5000
