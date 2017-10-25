#!/bin/bash
# Jenkins Notification build started
curl -H "Content-type: application/json" -X POST http://127.0.0.1:5000/v2.0/jenkins_notifications -d '{"name":"I-love-pizza", "build":{"full_url":"https://my_server/job/I-love-pizza/29/","number":29,"phase":"STARTED","parameters":{"DISABLE_CLEANUP":"false"}}}'
