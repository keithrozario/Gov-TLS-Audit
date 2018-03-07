import boto3
import json

import decimal
from boto3.dynamodb.types import DYNAMODB_CONTEXT
# Inhibit Inexact Exceptions
DYNAMODB_CONTEXT.traps[decimal.Inexact] = 0
# Inhibit Rounded Exceptions
DYNAMODB_CONTEXT.traps[decimal.Rounded] = 0


table_name = 'siteAudit'
table_key = 'hostname'
bucket_name = 'jangankenahack'
key_name = 'output.jsonl'


def remove_nulls(d):
    return {k: v for k, v in d.items() if v is not None and v != ''}


def insert_into_dynamo(event, context):

    # Get the service client
    s3 = boto3.client('s3')

    response = s3.get_object(Bucket=bucket_name, Key=key_name)
    file_data = response['Body'].read().decode('utf-8')
    jsons = file_data.split("\n")
    dict_jsons = []

    # Loads jsons into dict
    for json_data in jsons:
        if isinstance(json_data,str) and len(json_data) > 0:
            dict_jsons.append(json.loads(json_data,
                              object_hook=remove_nulls,
                              parse_float=str(),
                              parse_int=str(),
                              parse_constant=str()))

    # Table setup (first line for lambda, second line for local-machine test)
    # dynamodb = boto3.resource('dynamodb')  # for use in lambda
    dynamodb = boto3.resource('dynamodb',
                              region_name='us-west-2',
                              endpoint_url='https://dynamodb.us-west-2.amazonaws.com')
    table = dynamodb.Table('siteAudit')

    # write to table
    with table.batch_writer(overwrite_by_pkeys=['hostname', 'ip']) as batch:
        rowcount = 1
        for dict_json in dict_jsons:
            if isinstance(dict_json, list):  # empty rows in files get converted to empty list
                print("ERROR on row: " + str(rowcount))
            else:
                print("Row: " + str(rowcount))
                batch.put_item(Item=dict_json)

            rowcount += 1