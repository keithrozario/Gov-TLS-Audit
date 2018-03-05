import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr

table_name = 'siteAuditGovMy'
table_key = 'FQDN'

headers = {'Access-Control-Allow-Origin': '*'}  # allow CORS


# Decimal values were throwing too many errors
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


def get_by_fqdn(event, context):

    query_parameter = 'FQDN'

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # query parameter incorrect return statusCode=400
    if query_parameter not in event['queryStringParameters']:
        result = ''
        status_code = 400
    else:
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

    return {'statusCode': status_code,
            'headers': headers,
            'body': result}
