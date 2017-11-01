#!/bin/bash
# Jenkins Notification build started
curl -H "Content-type: application/json" -X POST http://127.0.0.1:5000/v2.0/jenkins_notifications -d '{"name":"DFG-compute-nova-8-unit-rhos", "build":{"full_url":"https://my_server/job/DFG-compute-nova-8-unit-rhos/3/","number":3,"phase":"STARTED","parameters":{"DISABLE_CLEANUP":"false", "GERRIT_BRANCH": "rhos-12.0-patches"}}}'
