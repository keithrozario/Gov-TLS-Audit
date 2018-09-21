import dns.resolver
import json
import datetime
import boto3
from botocore.exceptions import ClientError

headers = {'Access-Control-Allow-Origin': '*'}  # allow CORS
query_parameter = 'DN'
bucket_name = 'files.siteaudit.sayakenahack.com'
file_prefix = 'dns_records/'  # prefix to store results
file_extension = '.txt'


def query_dns_records(event, context):

    """
    Function Makes the Actual Query for the DNS records, and stores them as a file in S3
    It returns a body, status code & header, but is not actually exposed via API
    Make sure you call this with just a domain name, and not the FQDN
    """

    ids = ['SOA', 'TXT', 'MX', 'NS', 'DNSKEY']
    body = {'queryDate': (datetime.datetime.now(datetime.timezone.utc) +
                          datetime.timedelta(hours=8)).isoformat().upper()[:26],
            'queryRecords': ids}
    status_code = 200

    try:
        # Lower case the query
        fqdn = event['queryStringParameters'][query_parameter].lower()
        try:
            for record_type in ids:
                try:
                    answers = dns.resolver.query(fqdn, record_type)
                    records = []
                    for data in answers:
                        records.append(data.to_text())
                    body[record_type] = records

                except (dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.exception.Timeout):
                    pass  # might fail per record_type, perfectly fine

            # Upload file to  S3
            client = boto3.client('s3')
            result = json.dumps(body)
            client.put_object(Body=result.encode(), Bucket=bucket_name,
                              Key=file_prefix + fqdn + file_extension)
        except dns.resolver.NXDOMAIN:
            status_code = 404  # domain no longer exists, or domain not found :)
            result = ''

    except KeyError:  # insufficient queryStringParameters
        status_code = 400
        result = ''

    return {'statusCode': status_code,
            'headers': headers,
            'body': result}


def get_dns_records(event, context):

    try:
        fqdn = event['queryStringParameters'][query_parameter].lower()
        client = boto3.client('s3')
        result = client.get_object(Bucket=bucket_name,
                                   Key=file_prefix + fqdn + file_extension)
        body = result['Body'].read().decode('utf-8')
        status_code = 200

    except KeyError:
        status_code = 400  # query parameter not provided
        body = ''
    except ClientError:
        status_code = 404  # typically a file not found
        body = ''

    return {'statusCode': status_code,
            'headers': headers,
            'body': body}
