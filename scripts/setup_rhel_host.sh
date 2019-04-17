#!/bin/bash

# Install required packages for running the project
sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
sudo yum install -y httpd python-pip python-virtualenv gcc

# Modify firewall to allow traffic to port 80
sudo iptables -I INPUT 5 -i eth0 -p tcp --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT

# Install MongoDB
cat >/etc/yum.repos.d/mongodb-org.repo <<EOL
[MongoDB]
name=MongoDB Repository
baseurl=http://repo.mongodb.org/yum/redhat/\$releasever/mongodb-org/4.0/x86_64/
gpgcheck=0
enabled=1
EOL

yum install -y mongodb-org
systemctl start mongod
systemctl enable mongod
