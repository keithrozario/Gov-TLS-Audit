import boto3
import json
import tldextract
import urllib.request
import urllib.error
from botocore.exceptions import ClientError

query_parameter = 'DN'
bucket_name = 'files.siteaudit.sayakenahack.com'
file_prefix = 'hostnames/'  # prefix to store results
fqdn_file = 'fqdn.txt'
domain_file = 'domain.txt'
domain_to_fqdn_file = 'domain_to_fqdn.txt'
github_link = 'https://raw.githubusercontent.com/keithrozario/list_gov.my_websites/master/list.txt'
headers = {'Access-Control-Allow-Origin': '*'}  # allow CORS


def get_hostnames(event, context):

    """
    Gets list of FQDNs from github repo (where I store it)
    saves data into two text files, one for domains, and one for fqdns
    function is triggered daily -- refer to serverless.yml file
    """

    try:
        with urllib.request.urlopen(github_link) as response:
            content = response.read().decode(response.headers.get_content_charset())
        FQDNs = content.split("\n")
        # If newline at the end, delete it
        if FQDNs[-1] == '':
            del FQDNs[-1]

        # List FQDNs
        body_fqdn = json.dumps({"count": len(FQDNs), "FQDNs": FQDNs})

        # List Domains
        domains = []
        domain_to_fqdn = {}

        for FQDN in FQDNs:
            ext = tldextract.extract(FQDN)
            domains.append(ext.registered_domain)

            # store relationship of domain to FQDN
            try:
                domain_to_fqdn[ext.registered_domain].append(FQDN)
            except KeyError:
                domain_to_fqdn[ext.registered_domain] = []
                domain_to_fqdn[ext.registered_domain].append(FQDN)

        domains = list(set(domains))  # make unique (does not preserve order)
        body_domain = json.dumps({'count': len(domains), 'DNs': domains})
        body_relationship = json.dumps(domain_to_fqdn)

        client = boto3.client('s3')
        # Upload FQDN file to  S3
        client.put_object(Body=body_fqdn.encode(), Bucket=bucket_name,
                          Key=file_prefix + fqdn_file)

        # Upload Domain file to  S3
        client.put_object(Body=body_domain.encode(), Bucket=bucket_name,
                          Key=file_prefix + domain_file)

        # Upload domain to fqdn file to S3
        client.put_object(Body=body_relationship.encode(), Bucket=bucket_name,
                          Key=file_prefix + domain_to_fqdn_file)

        status_code = 200
    except urllib.error.HTTPError:
        status_code = 500
    except urllib.error.URLError:
        status_code = 500

    return status_code


def list_fqdns(event, context):

    try:
        client = boto3.client('s3')
        result = client.get_object(Bucket=bucket_name,
                                   Key=file_prefix + fqdn_file)
        body = result['Body'].read().decode('utf-8')
        status_code = 200
    except ClientError:
        status_code = 500
        body = ""

    return {'statusCode': status_code,
            'headers': headers,
            'body': body}


def list_domains(event, context):

    try:
        client = boto3.client('s3')
        result = client.get_object(Bucket=bucket_name,
                                   Key=file_prefix + domain_file)
        body = result['Body'].read().decode('utf-8')
        status_code = 200
    except urllib.error.HTTPError:
        status_code = 500
        body = ""
    except urllib.error.URLError:
        status_code = 500
        body = ""

    return {'statusCode': status_code,
            'headers': headers,
            'body': body}


def invoke_dns_queries(event, context):

    function_name = context.function_name  # the name of 'this' function
    env = function_name.split('-')[0]  # because of my naming convention, this will provide the env (SIT, Prod..etc)
    lambda_name = env + '-query_dns_records'  # name of lambda to invoke

    try:
        client = boto3.client('s3')
        result = client.get_object(Bucket=bucket_name,
                                   Key=file_prefix + domain_file)
        body = result['Body'].read().decode('utf-8')
        DNs = json.loads(body)['DNs']

        # Loop through each Domain name and query the dns
        error_domains = []
        lambda_client = boto3.client('lambda')
        for DN in DNs:
            payload = {"queryStringParameters": {"DN": DN}}
            lambda_client.invoke(FunctionName=lambda_name,
                                 InvocationType='Event',
                                 Payload=json.dumps(payload).encode()
                                )

        # if we reached here, then all is good
        if len(error_domains) == 0:
            return {'statusCode': 200,
                    'headers': headers,
                    'body': ''}
        else:
            return {'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'errors': error_domains})}

    except ClientError:  # because domain file does not exist
        return {'statusCode': 500,
                'headers': headers,
                'body': ''}
