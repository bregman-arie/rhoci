#!/bin/bash
virtualenv .venv && source .venv/bin/activate
pip install --upgrade .
rhoci run --debug
