import boto3
import decimal
import json
import urllib.request,urllib.error
from operator import itemgetter

headers = {'Access-Control-Allow-Origin': '*'}  # allow CORS


def list_scans(event, context):

    bucket_name = 'files.siteaudit.sayakenahack.com'
    file_prefix = 'files/'  # prefix to scan files from
    base_url = 'https://govscan.info/files/'
    keys = []
    status_code = 200

    client = boto3.client('s3')
    response = client.list_objects_v2(Bucket=bucket_name,
                                      Delimiter='|')

    for content in response['Contents']:
        if content['Key'][:len(file_prefix)] == file_prefix:
            file_name = content['Key'][len(file_prefix):]
            if file_name == '':
                continue  # S3 list bucket will return folder as an object (skip folder)
            else:
                url = base_url + file_name
                file_size = decimal.Decimal(content['Size'] / (1024 * 1024))
                file_size_string = str(round(file_size, 2)) + ' MB'
                keys.append({'fileName': file_name,
                             'url': url,
                             'fileSize': file_size_string})

    # sort by fileName, reverse to show latest file first
    keys_sorted = sorted(keys, key=itemgetter('fileName'), reverse=True)

    # Json needs to be string for API Gateway
    result = json.dumps({'files': keys_sorted})

    return {'statusCode': status_code,
            'headers': headers,
            'body': result}


def list_hostnames(event, context):

    url_of_hostnames = "https://raw.githubusercontent.com/keithrozario/list_gov.my_websites/master/list.txt"

    try:
        with urllib.request.urlopen(url_of_hostnames) as response:
            content = response.read().decode(response.headers.get_content_charset())
        FQDNs = content.split("\n")
        # If newline at the end, delete it
        if FQDNs[-1] == '':
            del FQDNs[-1]

        body = json.dumps({"FQDNs": FQDNs})
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