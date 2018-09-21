import tldextract
import json
import requests
import logging
import boto3
import custom_config

# Logging setup
logging.basicConfig(filename='dns_log.txt',
                    filemode='a',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)

# Get all fqdns
logger.info("Getting All Subdomains")
result = requests.get('https://govscan.info/api/v2/listFQDNs')
FQDNs = json.loads(result.text)
logger.info("%d SubDomains obtained" % len(FQDNs['FQDNs']))

# Get all unique domains
domains = []
for FQDN in FQDNs['FQDNs']:
    ext = tldextract.extract(FQDN)
    domains.append(ext.registered_domain)
domains = list(set(domains))  # make unique (does not preserve order)
logger.info("%d Unique Domains Found" % len(domains))

client = boto3.client('lambda', region_name=custom_config.aws_region)

for domain in domains:
    event = dict()
    event['queryStringParameters'] = {'DN': domain}
    response = client.invoke(
        FunctionName='SIT-query_dns_records',
        InvocationType='Event',
        Payload=json.dumps(event).encode()
    )
    logger.info("%s Called" % domain)
    # data = response['Payload'].read().decode('utf-8')
    # http_response = json.loads(data)
    # print(domain, " : ", http_response['body'])

