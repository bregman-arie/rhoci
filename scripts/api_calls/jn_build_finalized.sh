#!/bin/bash
# Jenkins Notification build finished to run
curl -H "Content-type: application/json" -X POST http://127.0.0.1:5000/api/jenkins_update -d '{"name":"DFG-test-comp_test-10-ceph", "build":{"full_url":"https://my_server/job/DFG-test-comp_test-10-ceph/3/","number":3,"parameters":{"DISABLE_CLEANUP":"false", "GERRIT_BRANCH": "rhos-12.0-patches"},"phase":"FINALIZED","status":"SUCCESS"}}'
