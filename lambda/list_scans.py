import boto3
import decimal
import json
from operator import itemgetter

headers = {'Access-Control-Allow-Origin': '*'}  # allow CORS


def list_scans(event, context):

    bucket_name = 'files.siteaudit.sayakenahack.com'
    base_url = 'https://siteaudit.sayakenahack.com/api/downloadScan?fileName='
    keys = []
    status_code = 200
    file_prefix = 'scan'

    client = boto3.client('s3')
    response = client.list_objects_v2(Bucket=bucket_name, Delimiter='|')

    for content in response['Contents']:
        if content['Key'][:4] == file_prefix:
            url = base_url + content['Key']
            file_size = decimal.Decimal(content['Size'] / (1024 * 1024))
            file_size_string = str(round(file_size, 2)) + ' MB'
            keys.append({'fileName': content['Key'],
                         'url': url,
                         'fileSize': file_size_string})

    # sort by fileName, reverse to show latest file first
    keys_sorted = sorted(keys, key=itemgetter('fileName'), reverse=True)

    # Json needs to be string for API Gateway
    result = json.dumps({'files': keys_sorted})

    return {'statusCode': status_code,
            'headers': headers,
            'body': result}
