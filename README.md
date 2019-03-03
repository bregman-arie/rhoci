# Red Hat OpenStack CI Dashboard

[![Build Status](https://travis-ci.org/bregman-arie/rhoci.svg?branch=refactor)](https://travis-ci.org/bregman-arie/rhoci)

RHOCI is Red Hat OpenStack CI Dashboard.

It's used for:

* Summarizing CI/CD results status in different levels (project, job, test)

## Quickstart

To run RHOCI server:

    rhoci-server

To run RHOCI Jenkins agent:

    rhoci-agent

Note: the agent used to populate the database with information gathered from Jenkins.

## The Tech Behind RHOCI

RHOCI is using several technologies:

* Flask
* Bootstrap
* Chart.js
