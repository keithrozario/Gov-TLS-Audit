import boto3
import base64
import botocore

headers = {'Access-Control-Allow-Origin': '*',  # allow CORS
           'Content-Type': 'application/zip',
           'Content-Disposition': 'attachment; '}  # zip Download


def download_zip(event, context):

    try:
        s3_bucket = 'files.siteaudit.sayakenahack.com'
        key = event['queryStringParameters']['fileName']
        tmp_file = '/tmp/' + key
        s3 = boto3.resource('s3')
        s3.Bucket(s3_bucket).download_file(key, tmp_file)

        with open(tmp_file, "rb") as fin:
            raw_data = fin.read()
            encoded = base64.b64encode(raw_data)  # encode everything into base64
            result = encoded.decode('ascii')  # now base64 to ascii

        # add filename to Content-Disposition header
        headers['Content-Disposition'] += 'filename = "' + key + '"'

        return {'statusCode': 200,
                'headers': headers,
                'isBase64Encoded': True,
                'body': result}

    except KeyError:  # parameter file not specified in request
        return {'statusCode': 400,
                'body': ''}

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return {'statusCode': 404,
                    'body': 'File Not Found'}
        else:
            return {'statusCode': 501,
                    'body': e.response['Error']['Code']}


