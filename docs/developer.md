# Developer Guide


## Installation

Prepare your host for installing the app and running it:

    scripts/setup_rhel_host.sh

Before running the server and the agent, you first need to set up a configuration (`/etc/rhoci/rhoci.conf`)
The most basic configuration is:

    jenkins:
      url: <Jenkins URL>
      user: <Jenkins username>
      password: <Jenkins API token>

Create a virtual environment where you will install the app:

    virtualenv ~/rhoci_venv && source ~/rhoci_venv/bin/activate
    pip install -r requirements.txt
    pip install .

To run RHOCI Jenkins agent, run the following:

    rhoci-agent

Once the configuration is in place, run the following command to start the server:

    rhoci-server

## Run RHOCI

Run the agent

    rhoci-agent

Run the server:

    rhoci-server
