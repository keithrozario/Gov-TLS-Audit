import dns.resolver
import json
import datetime
import boto3
from boto3.dynamodb.conditions import Key

headers = {'Access-Control-Allow-Origin': '*'}  # allow CORS
query_parameter = 'DN'
bucket_name = 'files.siteaudit.sayakenahack.com'
file_prefix = 'dns_records/'  # prefix to store results
file_extension = '.txt'
table_name = 'DNSRecords'


def query_dns_records(event, context):

    """
    Function Makes the Actual Query for the DNS records, and stores result in DynamoDB
    It returns a body, status code & header, but is **not** exposed via API
    Does not validate Domain name passed to it
    """
    ids = ['SOA', 'TXT', 'MX', 'NS', 'DNSKEY']
    dn = event['queryStringParameters'][query_parameter].lower()
    body = {'scanDate': (datetime.datetime.now(datetime.timezone.utc) +
                         datetime.timedelta(hours=8)).isoformat().upper()[:26],
            'scanRecordTypes': ids,
            'domain': dn,
            'records': {}}

    try:
        try:
            for record_type in ids:
                try:
                    answers = dns.resolver.query(dn, record_type)
                    records = []
                    for data in answers:
                        records.append(data.to_text())
                    body['records'][record_type] = records
                except (dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.exception.Timeout):
                    pass  # might fail per record_type, perfectly fine

            # insert into DynamoDB
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(table_name)
            table.put_item(Item=body)
            status_code = 200
            result = json.dumps(body)

        except dns.resolver.NXDOMAIN:
            status_code = 404  # domain no longer exists, or domain not found :)
            result = ''

    except KeyError:  # insufficient queryStringParameters
        status_code = 400
        result = ''

    return {'statusCode': status_code,
            'headers': headers,
            'body': result}


def get_dns_history(event, context):

    table_key = 'domain'
    query_parameter = 'DN'  # API Query parameter
    scan_date = 'scanDate'  # API Query parameter
    range_key = 'scanDate'  # DynamoDB range key

    # Default Values

    # upper case scan_date, or set scan_date to now
    try:
        scan_date_upper = event['queryStringParameters'][scan_date].upper()
    except KeyError:
        # Need to ensure UTC+8 in case lambda is running in US (other regions)
        scan_date_upper = (datetime.datetime.now(datetime.timezone.utc) +
                           datetime.timedelta(hours=8)).isoformat().upper()[:26]  # [:26] removes the timezone info

    # Limit search results
    try:
        limit = int(event['queryStringParameters']['limit'])
    except (ValueError, KeyError):
        limit = 30

    # Setup DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    try:
        # Lower case the query
        query_parameter_lower = event['queryStringParameters'][query_parameter].lower()
        # Query the DB
        response = table.query(KeyConditionExpression=Key(table_key).eq(query_parameter_lower) &
                                                      Key(range_key).lt(scan_date_upper),
                               Limit=limit,  # limit to 30 (default) or user supplied
                               ScanIndexForward=False)  # query in descending order (latest date first)

        if len(response['Items']) > 0:
            status_code = 200
            result = json.dumps({'results': response['Items']})
        else:
            status_code = 404  # no records found
            result = ''
    except KeyError:  # Insufficient Query String Parameters (no FQDN)
        status_code = 400
        result = ''

    return {'statusCode': status_code,
            'headers': headers,
            'body': result}
