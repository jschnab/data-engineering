#!/bin/bash
 
set -ex
set -o pipefail

exec > >(tee /var/log/user_data.log | logger -t user_data) 2>&1
echo BEGIN
BEGINTIME=$(date +%s)
date "+%Y-%m-%d %H:%M:%S"

HOME_FOLDER=/home/ec2-user

yum update -y
yum install -y git python3 gcc postgresql-devel python3-devel.x86_64

pip3 install psycopg2 bs4 pandas numpy matplotlib awscli boto3 paramiko jupyterlab easy-data-analysis

mkdir "$HOME_FOLDER"/.aws

cat << EOF > /home/ec2-user/.aws/config
[default]
region = us-east-1
output = json
EOF

JUPYTERLAB_PASSWORD=$(aws secretsmanager get-secret-value --secret-id jupyterlab_password --output text --query SecretString --region us-east-1)

mkdir "$HOME_FOLDER"/.jupyter
mkdir "$HOME_FOLDER"/notebooks

cat << EOF > "$HOME_FOLDER"/.jupyter/jupyter_notebook_config.py
c.NotebookApp.password = u"$JUPYTERLAB_PASSWORD"
c.NotebookApp.open_browser = False
c.NotebookApp.port = 8889
c.NotebookApp.ip = "*"
c.NotebookApp.notebook_dir = "$HOME_FOLDER/notebooks"
EOF

chown -R ec2-user:ec2-user "$HOME_FOLDER"

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
