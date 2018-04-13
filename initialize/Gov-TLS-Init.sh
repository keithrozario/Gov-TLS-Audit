#!/bin/bash
DIR=Gov-TLS-Audit
git clone https://github.com/keithrozario/Gov-TLS-Audit.git
mkdir $DIR/logs
mkdir $DIR/output
virtualenv $DIR/venv
source $DIR/venv/bin/activate
pip install -r $DIR/requirements.txt
echo "Don't forget to modify Shodan key location in custom_config.py to ../.shodan/key.txt"