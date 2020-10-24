#!/bin/bash
 
set -ex
set -o pipefail

exec > >(tee /var/log/user_data.log | logger -t user_data) 2>&1
echo BEGIN
BEGINTIME=$(date +%s)
date "+%Y-%m-%d %H:%M:%S"

yum update -y
yum install -y git python3 gcc postgresql-devel python3-devel.x86_64

pip3 install psycopg2 bs4 pandas numpy matplotlib awscli boto3 paramiko jupyterlab easy-data-analysis

mkdir /home/ec2-user/.aws

cat << EOF > /home/ec2-user/.aws/config
[default]
region = us-east-1
output = json
EOF

JUPYTERLAB_PASSWORD=$(aws secretsmanager get-secret-value --secret-id jupyterlab_password --output text --query SecretString)

mkdir /home/ec2-user/.jupyter
mkdir /home/ec2-user/notebooks

cat << EOF > /home/ec2-user/.jupyter/jupyter_notebook_config.py
c.NotebookApp.password = u"$JUPYTERLAB_PASSWORD"
c.NotebookApp.open_browser = False
c.NotebookApp.port = 8889
c.NotebookApp.ip = "*"
c.NotebookApp.notebook_dir = "/home/ec2-user/notebooks"
EOF

chown -R ec2-user:ec2-user /home/ec2-user

cat << EOF > /etc/systemd/system/jupyterlab.service
[Unit]
Description=Jupyterlab server
After=network.target

[Service]
User=ec2-user
Group=ec2-user
Type=simple
ExecStart=/usr/local/bin/jupyter lab
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

systemctl enable jupyterlab.service
systemctl start jupyterlab.service

date "+%Y-%m-%d %H:%M:%S"
ENDTIME=$(date +%s)
echo "deployment took $((ENDTIME - BEGINTIME)) seconds"
echo END
