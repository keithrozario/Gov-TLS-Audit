import logging
import boto3


def delete_table(dynamoClient, tableName):
    response = dynamoClient.list_tables()

    if tableName in response['TableNames']:

        response = dynamoClient.describe_table(TableName=tableName)

        logger.info("WARNING: Table with name " + tableName + " found. Proceed to delete?")
        logger.info("Name: " + response['Table']['TableName'])
        logger.info("RowCount: " + str(response['Table']['ItemCount']))
        logger.info("CreationDate: " + str(response['Table']['CreationDateTime']))

        response = dynamoClient.delete_table(TableName=tableName)
        logger.info("INFO: Table " + response['TableDescription']['TableName'] + "deleted")
    else:
         logger.info("INFO: Table Not Found")

    return


def create_table(dynamoClient, tableName, keyHash, keyHashType, keyRange, keyRangeType):
    response = dynamoClient.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': keyHash,
                'AttributeType': keyHashType

            },
            {
                'AttributeName': keyRange,
                'AttributeType': keyRangeType

            }

        ],
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': keyHash,
                'KeyType': 'HASH'
            },
            {
                'AttributeName': keyRange,
                'KeyType': 'RANGE'
            }
        ],
        ProvisionedThroughput=
        {
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 10,
        })

    logger.info("GOOD: Table " + response['TableDescription']['TableName'] + " created on " + \
                str(response['TableDescription']['CreationDateTime']) + \
                "\n" + str(response['TableDescription']['KeySchema']))


def initialize_table(dynamoDB, tableName, keyHash, keyHashType, keyRange, keyRangeType):
    dynamoClient = dynamoDB.meta.client
    delete_table(dynamoClient, tableName)
    create_table(dynamoClient, tableName, keyHash, keyHashType, keyRange, keyRangeType)


########################################################################################################################
#     MAIN                                                                                                             #
########################################################################################################################

if __name__ == "__main__":

    LogFileName = 'log.txt'
    LogLevel = logging.INFO
    LogFileMode = 'a'
    LogMsgFormat = '%(asctime)s %(message)s'
    LogDateFormat = '%m/%d/%Y %I:%M:%S %p'

    # Logging setup
    logging.basicConfig(filename=LogFileName, filemode=LogFileMode, level=LogLevel, format=LogMsgFormat,
                        datefmt=LogDateFormat)
    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    # Table setup
    dynamodb = boto3.resource('dynamodb',
                              region_name='us-west-2',
                              endpoint_url="https://dynamodb.us-west-2.amazonaws.com")

    tableName = 'siteAudit'
    keyHash = 'hostname'
    keyHashType = 'S'
    keyRange = "ip"
    keyRangeType = "S"

    # WARNING: initDB will delete any old DB's
    initialize_table(dynamodb, tableName, keyHash, keyHashType, keyRange, keyRangeType)