# RHOCI

[![Build Status](https://travis-ci.org/bregman-arie/rhoci.svg?branch=master)](https://travis-ci.org/bregman-arie/rhoci)

RHOCI (Red Hat OpenStack CI)

* [Requirements](#requirements)
* [Installation](#installation)
* [Getting Started](#getting-started)
* [Configuration](#configuration)

## Requirements

* Python >= 2.7

## Installation

    virtualenv .venv && source .venv/bin/activate
    pip install .

You can also run the quick setup script in this directory:

    chmod +x scripts/quick_run.sh && scripts/quick_run.sh

## Run RHOCI

    rhoci run

## Configuration 

The default location for RHOCI configuration is '/etc/rhoci/rhoci.conf'.
You can specify it by using the CLI: --conf <conf_file_path>

You can find sample in samples/rhoci.conf

## The technologies behind Jino

* Flask
* SQLite
* Patternfly
