# ServerSide Deployment

This is the 'server' side deployment for siteaudit.sayakenahack.com. Including DynamoDB, S3, ApiGateway and Lambda functions.

In theory there are no *servers*, but code here is for what is traditionally understood to be the back-end Server side.

Deployed using the [serverless framework](https://serverless.com). Refer to the serverless.yml file for details. 

## S3 Bucket

Single bucket used to store all incremental scan data in csv, jsonl and json file formats. Every scan has one zip file that contains all 3 formats in it.

Bucket is non-public accessible, and all access is through the API Gateway call

## DynamoDB

DB for all scans (ever!). All scans are stored in DynamoDB at maximum verbosity (every field)

## API Gateway & Lambda

All API Gateway calls invoke one(and only one) lambda function. All lambda functions are tied to just one API call. If this changes, I'll update the documentation format, but it's easier to document them in one section fo now.

## Lambda

Lambda functions are written in Python 3.6, and have their own requirements.txt file present here. Do not use the requirements.txt from the main folder, your functions will be massive.

## Proper Documentation

To use the api, refer to the API docs [here](https://govscan.info/docs/index.html).

## Test Scripts

`test_dev.sh` and `test_prod.sh` are bash files that invoke the lambda functions with test data stored in the test/ folder.

`test_prod.sh` will also call the API Gateway endpoints using curl and wget commands. There is an open issue to include this functionality into `test_dev.sh`

\* *currently only two stages are present. Dev and Prod (case-sensitive)*