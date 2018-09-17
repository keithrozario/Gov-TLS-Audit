#!/bin/bash
DIR=~/Code/Gov-TLS-Audit

rm $DIR/output/full_output.json
rm $DIR/output/output.csv
rm $DIR/output/output.jsonl
source $DIR/venv/bin/activate
cd $DIR
python scan.py
python insert_jsonl_into_dynamo.py
python house_keeping.py