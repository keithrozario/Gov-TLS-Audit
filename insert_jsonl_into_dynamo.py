import zipfile
import datetime
import custom_config
import boto3
import logging
import json
import decimal
import time

from botocore.exceptions import ClientError
from boto3.dynamodb.types import DYNAMODB_CONTEXT

# Inhibit Inexact Exceptions
DYNAMODB_CONTEXT.traps[decimal.Inexact] = 0
# Inhibit Rounded Exceptions
DYNAMODB_CONTEXT.traps[decimal.Rounded] = 0


def zip_file():

    object_name = custom_config.obj_prefix + datetime.date.today().isoformat() + '.zip'

    output_dir = 'output/'
    jsonl_name = 'output.jsonl'
    json_name = 'full_output.json'
    csv_name = 'output.csv'

    with zipfile.ZipFile(output_dir + object_name, 'w') as myzip:
        myzip.write(custom_config.json_file,
                    arcname=jsonl_name,
                    compress_type=zipfile.ZIP_DEFLATED)
        myzip.write(custom_config.full_json_file,
                    arcname=json_name,
                    compress_type=zipfile.ZIP_DEFLATED)
        myzip.write(custom_config.csv_file,
                    arcname=csv_name,
                    compress_type=zipfile.ZIP_DEFLATED)

    return object_name


def upload_to_s3(object_name, s3_dir_name=None, local_dir_name=custom_config.output_dir):

    if s3_dir_name is None:
        object_path = custom_config.s3_upload_dir + "/" + object_name
    else:
        object_path = s3_dir_name + "/" + object_name

    # S3 setup
    s3 = boto3.resource('s3')  # need resource for meta.client.upload_file
    s3.meta.client.upload_file(local_dir_name + object_name,
                               custom_config.bucket_name,
                               object_path,
                               )


def remove_nulls(d):
    return {k: v for k, v in d.items() if v is not None and v != ''}


def update_table(dynamo_client, table_name, write_capacity):

    try:
        logger.info("Checking Table")
        response = dynamo_client.describe_table(TableName=table_name)
        read_capacity = response['Table']['ProvisionedThroughput']['ReadCapacityUnits']
        logger.info("INFO: Table Read Capacity: " + str(read_capacity))
        logger.info("INFO: Current Write Capacity: " + str(response['Table']['ProvisionedThroughput']['WriteCapacityUnits']))
        logger.info("INFO: Updating Write Capacity to: " + str(write_capacity))
        response = dynamo_client.update_table(
                TableName=table_name,
                ProvisionedThroughput=
                {
                'WriteCapacityUnits': write_capacity,
                'ReadCapacityUnits': read_capacity
                })
        logger.info("INFO: Update Complete")
    except ClientError:
        logger.info("WARNING: Unable to Update Table")
        return 0

    logger.info("GOOD: Table " + response['TableDescription']['TableName'] + " updated")
    logger.info("INFO: Table info -- ")


def insert_into_dynamo():

    # Table setup
    dynamo_db = boto3.resource('dynamodb',
                               region_name=custom_config.aws_region,
                               endpoint_url=custom_config.endpoint_url)
    table = dynamo_db.Table(custom_config.dynamo_table_name)
    dynamo_client = dynamo_db.meta.client

    update_table(dynamo_client,
                 custom_config.dynamo_table_name,
                 custom_config.dynamo_table_write_capacity)

    with open(custom_config.json_file, 'r') as f:
        rows = f.readlines()

    with table.batch_writer() as batch:
        # load each json to a record, and append to json_records
        for row in rows:
            try:
                record = json.loads(row,
                                    object_hook=remove_nulls,
                                    parse_float=str(),  # needed to avoid exception thrown
                                    parse_int=str(),  # needed to avoid exception thrown
                                    parse_constant=str())
                record['dateAdded'] = datetime.date.today().isoformat()
                batch.put_item(Item=record)
                logger.info('Record: ' + record['FQDN'] + ' put to DB')

            except AttributeError:
                logger.info("ERROR: Attribute Error on row")

    # Update write capacity back to 1
    update_table(dynamo_client,
                 custom_config.dynamo_table_name,
                 1)
    logger.info('Total rows written:' + str(len(rows)))

    # wait 2 minute before beginning backup as
    # "On-Demand Backup does not support causal consistency"
    logger.info('Waiting 2 minutes before backing up table')
    time.sleep(120)

    # begin backup
    backup_name = custom_config.dynamo_table_backup_prefix + str(datetime.date.today().isoformat())
    response = dynamo_client.create_backup(TableName=custom_config.dynamo_table_name,
                                           BackupName=backup_name)
    logger.info("Backup Status: " + response['BackupDetails']['BackupStatus'])
    logger.info("Backup Size: " + str(response['BackupDetails']['BackupSizeBytes']))
    logger.info("Backup TimeStamp: " + str(response['BackupDetails']['BackupCreationDateTime']))


def upload_and_write():
    logger.info("Zipping Files")
    object_name = zip_file()
    logger.info("Uploading to S3 Bucket: " + object_name)
    upload_to_s3(object_name)
    logger.info("Writing to DynamoDB")
    insert_into_dynamo()
    logger.info("Uploading logs S3 Bucket: logs/scan.log")
    logger.info("DONE")
    upload_to_s3("scan.log", "logs", "logs/")
    logger.info("DONE Uploading")


if __name__ == "__main__":
    # Logging setup
    logging.basicConfig(filename='logs/upload.log',
                        filemode='w',
                        level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')

    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)
    upload_and_write()