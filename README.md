# RHOCI

[![Build Status](https://travis-ci.org/bregman-arie/rhoci.svg?branch=master)](https://travis-ci.org/bregman-arie/rhoci)

RHOCI (Red Hat OpenStack CI)

A web service based on Jenkins to enhance user experience for Red Hat OpenStack CI users.
This project allows you to:

    * Display information on all jobs without loading additional pages
    * Compare test results of two different builds of the same job
    * Generate job definitions based on given input
    * Trigger jobs based on component name and release

And more :)

* [Requirements](#requirements)
* [Installation](#installation)
* [Getting Started](#getting-started)
* [Configuration](#configuration)
* [API](#api)

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

## API

API is documented in /doc view and generated automatically

## The technologies behind RHOCI

* Flask
* SQLite
* Patternfly

## Overview

<div align="center"><img src="./doc/rhoci_overview.png" alt="RHOCI Overview"></div><hr />

## Screenshots

### Home page

<div align="center"><img src="./doc/home_page.png" alt="RHOCI Home Page"></div><hr />

### Jobs page

<div align="center"><img src="./doc/jobs_page.png" alt="RHOCI Jobs Page"></div><hr />

## How to add a new page

* Create the html templates in rhoci/rhoci/templates/<new_page_name>.html
* Add a new entry in rhoci/rhoci/views/__init__.py
* Add a new view in rhoci/rhoci/views/<new_page_name>.html
* Add a new item to 'views' variable in rhoci/rhoci/web.py
* Add it to the navigation bar in rhoci/rhoci/templates/navbar.html
