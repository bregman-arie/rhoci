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

    rhoci-server

## Configuration 

RHOCI loads configuration in this order:

    Default config.py - built-in. Part of RHOCI code base.
    Environment varliabes - any of the environment vairables specified in the table below that the user export (e.g. `export RHOCI_SERVER_PORT=80`)
    Configurtion file - the default configuration file (/etc/rhoci/server.conf) or the file you mentioned with parser/environment variable.
    Parser - arguments you pass with rhoci command-line invocation.

| Name | Description | Required |
| ---- | ----------- | -------- |
| `RHOCI_JENKINS_URL` | Jenkins URL | Yes
| `RHOCI_JENKINS_USER` | Jenkins username | Yes
| `RHOCI_JENKINS_PASSWORD` | Jenkins username | Yes
| `RHOCI_CONFIG_FILE` | The configuration file from where to load additional configuration | No
| `RHOCI_DEBUG` | Turn on DEBUG | No
| `RHOCI_SERVER_PORT` | The port to use when running RHOCI server | No

A sample can be found in samples/server.conf

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

## How to add a new page

* Create the html templates in rhoci/rhoci/templates/<new_page_name>.html
* Add a new entry in rhoci/rhoci/views/__init__.py
* Add a new view in rhoci/rhoci/views/<new_page_name>.html
* Add a new item to 'views' variable in rhoci/rhoci/web.py
* Add it to the navigation bar in rhoci/rhoci/templates/navbar.html
