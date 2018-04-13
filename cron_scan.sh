#!/bin/bash

rm output/full_output.json
rm output/output.csv
rm output/output.jsonl
source venv/bin/activate
python scan.py
python insert_jsonl_into_dynamo.py