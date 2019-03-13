#!/bin/bash

# This will continue running current existing server without removing anything

source .venv/bin/activate
pip install --upgrade .
rhoci-server --debug -p 5000
