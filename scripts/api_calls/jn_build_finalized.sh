#!/bin/bash
# Jenkins Notification build finished to run
curl -H "Content-type: application/json" -X POST http://127.0.0.1:5000/api/jenkins_update -d '{"name":"DFG-network-neutron-33-unit-rhos", "build":{"full_url":"https://my_server/job/DFG-network-neutron-33-unit-rhos/302/","number":302,"parameters":{"DISABLE_CLEANUP":"false", "GERRIT_BRANCH": "rhos-12.0-patches"},"phase":"FINALIZED","status":"BLABLA"}}'
