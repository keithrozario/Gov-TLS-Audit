import boto3
import decimal
import json
from operator import itemgetter

headers = {'Access-Control-Allow-Origin': '*'}  # allow CORS
bucket_name = 'files.siteaudit.sayakenahack.com'
file_prefix = 'files/'


def list_scans(event, context):

    base_url = 'https://govscan.info/files/'
    keys = []
    status_code = 200

    client = boto3.client('s3')
    response = client.list_objects_v2(Bucket=bucket_name,
                                      Prefix=file_prefix)

    for content in response['Contents']:
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
    result = json.dumps({'files': keys_sorted,
                         'count': len(keys_sorted)})

    return {'statusCode': status_code,
            'headers': headers,
            'body': result}
