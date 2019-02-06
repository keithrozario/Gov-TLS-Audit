import boto3
import operator
import logging
from datetime import datetime, timedelta, timezone

# DynamoDB
retirement_age = 3  # Only delete backups older than this many days (caveat: max_backups)
max_backups = 2  # keep at least this many backups present (regardless of age)
table_name = 'siteAuditGovMy'

# S3
file_max_backups = 2 # always keep at least these many backups
file_retirement_age = 7  # Only archive zip files after their this many days old
archive_directory = 'archives'
s3_upload_dir = "files"
bucket_name = 'files.siteaudit.sayakenahack.com'

timezone_delta = 8

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def clean_up(event, context):

    '''
    Script deletes all backups, except the <x> latest backups, and any backup younger than retirement_age.
    where <x> is max_backups.
    If you take daily backups, retirement_age should equal max_backups
    '''

    upper_bound = (datetime.now(timezone(timedelta(hours=timezone_delta))) - timedelta(days=retirement_age))

    # Query API for list of backups for table
    client = boto3.client('dynamodb')
    logger.info("Querying Backups for table: %s" % table_name)
    response = client.list_backups(TableName=table_name)
    logger.info("Response received, %d backups found" % len(response['BackupSummaries']))

    # Sort response (latest backups first)
    response['BackupSummaries'].sort(key=operator.itemgetter('BackupCreationDateTime'), reverse=True)

    # Loop through, but skip latest backups (from <max_backups> onwards)
    for backup in response['BackupSummaries'][max_backups:]:

        # Delete the backup if it's older than retirement_age
        if backup['BackupCreationDateTime'] < upper_bound:
            logger.info("Deleting backup: %s dated %s" % (backup['BackupArn'], backup['BackupCreationDateTime']))
            response = client.delete_backup(BackupArn=backup['BackupArn'])
            logger.info('Deletion Successful: %s ' % response['BackupDescription']['BackupDetails'])

    # Get latest list (post-deletion)
    response = client.list_backups(TableName=table_name)
    for backup in response['BackupSummaries']:
        logger.info('Retained Backup: %s ' % backup)

    file_upper_bound = (datetime.now(timezone(timedelta(hours=timezone_delta))) - timedelta(days=file_retirement_age))

    # list out scans in S3 bucket
    logger.info("Retrieving list of files in S3 bucket")
    client = boto3.client('s3')
    file_prefix = s3_upload_dir + "/"
    response = client.list_objects_v2(Bucket=bucket_name,
                                      Prefix=file_prefix)

    # Sort response (latest files first)
    response['Contents'].sort(key=operator.itemgetter('LastModified'), reverse=True)

    # loop through only backups after max_backup:
    for content in response['Contents'][file_max_backups:]:
        file_name = content['Key'][len(file_prefix):]

        if file_name == '':
            continue  # S3 list bucket will return folder as an object (skip folder)
        else:
            if content['LastModified'] < file_upper_bound:
                # Archive file
                client.copy({'Bucket': bucket_name, 'Key': content['Key']},
                            bucket_name, archive_directory + '/' + file_name)
                logger.info("%s : Archived" % file_name)
                # Delete file
                response = client.delete_object(Bucket=bucket_name,
                                                Key=content['Key'])
                if response['DeleteMarker']:
                    logger.info("Successfully Deleted %s" % file_name)
                else:
                    logger.info("Unable to delete %s" % file_name)

    return {"status": 200,
            "Message": "Success"}