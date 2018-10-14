import boto3
import json
import hmac
import hashlib
from botocore.exceptions import ClientError

headers = {'Access-Control-Allow-Origin': '*'}


def get_secret():
    secret_name = "prod/govScan/secrets"
    secret_region = "us-west-2"  # hard-code region

    client = boto3.client('secretsmanager', region_name=secret_region)

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        secret = None
    else:
        secret = get_secret_value_response['SecretString']

    return secret


def check_sig(payload, sig):

    secret = json.loads(get_secret())

    if secret is None:  # issues retrieving secret -- mark to False
        return {'status': False, 'Error': 'Unable to retrieve secret'}
    else:
        h1 = hmac.new(bytearray(secret['github_secret'], 'utf-8'),
                      bytearray(payload, 'utf-8'),
                      hashlib.sha1)

        if hmac.compare_digest(h1.hexdigest(), sig[5:]):
            return {'status': True}
        else:
            return {'status': False, 'Error': 'Digest does not match'}


def receive_github_post(event, context):

    """
    Receives a POST from github, verifies the signature and message before invoking the get_hostnames function
    get_hostnames is invoked asynchrously, and a 202 status message is returned to github
    signature verification is done via a secret in secrets manager
    """

    github_event = event['headers']['X-GitHub-Event']
    sig = event['headers']['X-Hub-Signature']
    result = check_sig(event['body'], sig)

    if not result['status']:  # Digest did not match
        return {'statusCode': 403,
                'headers': headers,
                'body': json.dumps(result)}
    else:

        # only process if it's a push event and the push affected the head of Master
        if github_event == 'push':
            lambda_client = boto3.client('lambda')
            function_name = context.function_name  # the name of 'this' function
            env = function_name.split('-')[0]  # because of my naming convention, this will provide the env
            lambda_name = env + '-get_hostnames'  # name of lambda to invoke
            response = lambda_client.invoke(FunctionName=lambda_name,
                                            InvocationType='Event',
                                            Payload=json.dumps('').encode())
            status_code = response['StatusCode']
            body = ''
        else:
            status_code = 200
            body = ''
        return {'statusCode': status_code,
                'headers': headers,
                'body': json.dumps(body)}