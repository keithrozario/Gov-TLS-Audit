import boto3
import operator
import logging
from datetime import datetime, timedelta, timezone
import custom_config

'''
Script deletes all backups, except the <x> latest backups, and any backup younger than retirement_age.
where <x> is max_backups.
If you take daily backups, retirement_age should equal max_backups
'''

# Logging setup
logging.basicConfig(filename='logs/house_keeping.log',
                    filemode='a',  # file gets uploaded to S3 at end of run
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)


upper_bound = (datetime.now(timezone(timedelta(hours=custom_config.timezone_delta)))
               - timedelta(days=custom_config.retirement_age))

# Query API for list of backups for table
client = boto3.client('dynamodb')
logger.info("Querying Backups for table: %s" % custom_config.dynamo_table_name)
response = client.list_backups(TableName=custom_config.dynamo_table_name)
logger.info("Response received, %d backups found" % len(response['BackupSummaries']))

# Sort response (latest backups first)
response['BackupSummaries'].sort(key=operator.itemgetter('BackupCreationDateTime'), reverse=True)

# Loop through, but skip latest backups (from <max_backups> onwards)
for backup in response['BackupSummaries'][custom_config.max_backups:]:

    # Delete the backup if it's older than retirement_age
    if backup['BackupCreationDateTime'] < upper_bound:
        logger.info("Deleting backup: %s dated %s" % (backup['BackupArn'], backup['BackupCreationDateTime']))
        response = client.delete_backup(BackupArn=backup['BackupArn'])
        logger.info('Deletion Successful: %s ' % response['BackupDescription']['BackupDetails'])

# Get latest list (post-deletion)
response = client.list_backups(TableName=custom_config.dynamo_table_name)
for backup in response['BackupSummaries']:
    logger.info('Retained Backup: %s ' % backup)