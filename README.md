# RHOCI

[![Build Status](https://travis-ci.org/bregman-arie/rhoci.svg?branch=master)](https://travis-ci.org/bregman-arie/rhoci)

RHOCI (Red Hat OpenStack CI)

A web service that meant to enhance Jenkins user experience for Red Hat OpenStack CI users.
There is an effort to create a more generic project [here](https://github.com/bregman-arie/infuse) that will allow you to use it with any Jenkins server.

Some of the things this project allows you to do:

    * View all jobs in one datatable where you can filter them based on different parameters
    * View all builds in one datatable where you can filter them based on different parameters
    * View all unique tests and how many times they failed or passed
    * Generate job definitions based on given input

* [Requirements](#requirements)
* [Installation](#installation)
* [Getting Started](#getting-started)
* [Configuration](#configuration)
* [API](#api)

## Requirements

* Python >= 2.7

## Installation

    sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
    sudo yum install -y httpd python-pip python-virtualenv gcc
    virtualenv .venv && source .venv/bin/activate
    pip install .

Note that you can instead run the following two scripts

    chmod +x scripts/initial_setup.sh && scripts/initial_setup.sh
    chmod +x scripts/quick_run.sh && scripts/quick_run.sh

## Run RHOCI

    rhoci run

## Configuration 

Configuration precedence is as follows

    Environment variable start with 'RHOCI_'
    CLI parameters as provided by the user
    Configuration file (default or as provided by user)

The default location for RHOCI configuration is '/etc/rhoci/rhoci.conf'.
You can specify it by using the CLI: --conf <conf_file_path>

A sample can be found in samples/rhoci.conf

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
