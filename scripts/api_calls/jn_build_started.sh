#!/bin/bash
# Jenkins Notification build started
curl -H "Content-type: application/json" -X POST http://127.0.0.1:5000/api/jenkins_update -d '{"name":"DFG-test-comp_test-11-ceph", "build":{"full_url":"https://my_server/job/DFG-test-comp_test-10-ceph/3/","number":3,"phase":"what","parameters":{"DISABLE_CLEANUP":"false", "GERRIT_BRANCH": "rhos-12.0-patches"}}}'
