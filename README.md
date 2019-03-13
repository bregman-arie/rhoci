# Red Hat OpenStack CI Dashboard

[![Build Status](https://travis-ci.org/bregman-arie/rhoci.svg?branch=master)](https://travis-ci.org/bregman-arie/rhoci)

RHOCI is Red Hat OpenStack CI Dashboard.

## Quick start

Before running the server and the agent, you first need to set up a configuration (`/etc/rhoci/rhoci.conf`)
The most basic configuration is:

jenkins:
  url: <Jenkins URL>
  user: <Jenkins username>
  password: <Jenkins API token>

Once the configuration is in place, run the following command to start the server:

    rhoci-server

To run RHOCI Jenkins agent, run the following:

    rhoci-agent

## Developer Guide

Whould like to contribute to RHOCI? click [here](docs/developer.md)
