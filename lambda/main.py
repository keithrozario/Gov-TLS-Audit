import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

# Block below is required to avoid Decimal errors in DynamoDB
import decimal
from boto3.dynamodb.types import DYNAMODB_CONTEXT
# Inhibit Inexact Exceptions
DYNAMODB_CONTEXT.traps[decimal.Inexact] = 0
# Inhibit Rounded Exceptions
DYNAMODB_CONTEXT.traps[decimal.Rounded] = 0

table_name = 'siteAuditGovMy'
table_key = 'FQDN'

headers = {'Access-Control-Allow-Origin': '*'}  # allow CORS


# Decimal values were throwing too many errors
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


def get_latest_fqdn(event, context):

    query_parameter = 'FQDN'

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    try:
        # Lower case the query
        query_parameter_lower = event['queryStringParameters'][query_parameter].lower()
        # Query the DB
        response = table.query(KeyConditionExpression=Key(table_key).eq(query_parameter_lower),
                               Limit=1,  # Get only one record
                               ScanIndexForward=False)  # query in descending order

        if len(response['Items']) > 0:
            status_code = 200
            result = json.dumps(response['Items'], cls=DecimalEncoder)
        else:
            status_code = 404
            result = ''

    except KeyError:  # insufficient queryStringParameters
        status_code = 400
        result = ''

    return {'statusCode': status_code,
            'headers': headers,
            'body': result}


def get_scan(event, context):

    query_parameter = 'FQDN'
    scan_parameter = 'scanDate'
    range_key = 'scanDate'

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    try:
        # Lower case the query
        query_parameter_lower = event['queryStringParameters'][query_parameter].lower()
        # Upper 'T' in isoformat DateTime
        scan_parameter_upper = event['queryStringParameters'][scan_parameter].upper()
        # Query the DB
        response = table.query(KeyConditionExpression=Key(table_key).eq(query_parameter_lower) &
                                                      Key(range_key).eq(scan_parameter_upper),
                               Limit=1,  # Get only one record
                               ScanIndexForward=False)  # query in descending order

        if len(response['Items']) > 0:
            status_code = 200
            result = json.dumps(response['Items'], cls=DecimalEncoder)
        else:
            status_code = 404
            result = ''
    except KeyError:
        status_code = 400
        result = ''

    return {'statusCode': status_code,
            'headers': headers,
            'body': result}


def get_history_fqdn(event, context):

    query_parameter = 'FQDN'

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # query parameter incorrect return statusCode=400
    try:
        # Lower case the query
        query_parameter_lower = event['queryStringParameters'][query_parameter].lower()
        # Query the DB
        response = table.query(KeyConditionExpression=Key(table_key).eq(query_parameter_lower),
                               Limit=50,  # Get only 50 records
                               ScanIndexForward=False)  # query in descending order

        if len(response['Items']) > 0:
            scans = []
            for item in response['Items']:
                scan_data = {'scanDate': item['scanDate'][:10],
                             'scanDateTime': item['scanDate'],
                             'TLSRedirect': item.get('TLSRedirect', 'n/a'),
                             'TLSSiteExist': item.get('TLSSiteExist', 'n/a'),
                             'htmlSize': item['httpResponse'].get('htmlSize', 'n/a'),
                             'siteTitle': item.get('siteTitle', 'n/a')}
                scans.append(scan_data)
            status_code = 200
            result = json.dumps({'results': scans}, cls=DecimalEncoder)

        else:
            status_code = 404
            result = ''
    except KeyError:  # Insufficient Query String Parameters
        status_code = 400
        result = ''

    return {'statusCode': status_code,
            'headers': headers,
            'body': result}
