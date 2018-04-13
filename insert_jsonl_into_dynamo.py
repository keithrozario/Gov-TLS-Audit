import zipfile
import datetime
import custom_config
import boto3
import logging
import json
import decimal

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


def insert_into_dynamo():

    # Table setup
    dynamo_db = boto3.resource('dynamodb',
                               region_name=custom_config.aws_region,
                               endpoint_url=custom_config.endpoint_url)
    table = dynamo_db.Table(custom_config.dynamo_table_name)

    with open(custom_config.json_file, 'r') as f:
        jsons = f.readlines()

    # load each json to a record, and append to json_records
    counter = 0
    for row in jsons:
        counter += 1
        try:
            record = json.loads(row,
                                object_hook=remove_nulls,
                                parse_float=str(),  # needed to avoid exception thrown
                                parse_int=str(),  # needed to avoid exception thrown
                                parse_constant=str())
            record['dateAdded'] = datetime.date.today().isoformat()
            table.put_item(Item=record)
            logger.info('Record: ' + record['FQDN'] + ' put to DB')

        except AttributeError:
            pass

    logger.info('Total rows written:' + str(counter))


def upload_and_write():
    logger.info("Zipping Files")
    object_name = zip_file()
    logger.info("Uploading to S3 Bucket: " + object_name)
    upload_to_s3(object_name)
    logger.info("Uploading logs S3 Bucket: logs/scan.log")
    upload_to_s3("scan.log", "logs", "logs/")
    logger.info("Writing to DynamoDB")
    insert_into_dynamo()
    logger.info("DONE")


if __name__ == "__main__":
    # Logging setup
    logging.basicConfig(filename='logs/upload.log',
                        filemode='a',
                        level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')

    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)
    upload_and_write()