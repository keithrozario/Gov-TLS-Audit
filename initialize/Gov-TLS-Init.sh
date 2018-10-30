#!/bin/bash
DIR=Gov-TLS-Audit
export LC_ALL=C
apt update
apt install python-pip
apt install python3-pip
apt-get install python3-venv
pip install virtualenv
git clone https://github.com/keithrozario/Gov-TLS-Audit.git
mkdir $DIR/logs
mkdir $DIR/output
python3 -m venv $DIR/venv
source $DIR/venv/bin/activate
export LC_ALL=C
pip install wheel
pip install --upgrade pip
pip install -r $DIR/requirements.txt
deactivate
echo "Setting correct time zone and restarting crontab"
timedatectl set-timezone Asia/Singapore
sudo service cron restart
echo "Installing AWSCLI"
pip install awscli --upgrade --user
apt install awscli
aws configure
echo "Don't forget to modify Shodan key location in custom_config.py to ../.shodan/key.txt"