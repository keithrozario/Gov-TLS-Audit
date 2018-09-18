import requests
import json
import tldextract
import time
import logging
from custom_config import facebook_key_file


def get_CN(subject):
    names  = subject.split('/')
    for name in names:
        if name[:3] == 'CN=':
            return name[3:]
    return 'error-with-CN.com'


def call_api(payload, endpoint):
    # Call Facebook Graph API
    logger.info("Calling Facebook API")
    response = requests.get(endpoint, params=payload)

    while response.status_code == 403:
        logger.info("Status Code 403 received (rate-limit on FB), waiting 15 minutes to try again")
        time.sleep(15*60)  # wait 15 minutes try again
        response = requests.get(endpoint, params=payload)

    return response


def check_domain(domain, key):
    api_endpoint = "https://graph.facebook.com/v3.1/certificates"
    payload = {'fields': 'subject_name,domains',
               'access_token': key,
               'query': domain}

    results = []

    logger.info("Calling API for %s" % domain)
    response = call_api(payload, api_endpoint)
    result = json.loads(response.text)
    if len(result['data']) == 0:
        return None  # no data on domain
    results.extend(result['data'])
    logger.info("Found %d results for %s" % (len(result['data']), domain))

    # Page through all results
    while 'paging' in result and 'next' in result['paging']:
        logger.info("Calling API for %s : Paging" % domain)
        payload['after'] = result['paging']['cursors']['after']
        response = call_api(payload, api_endpoint)
        result = json.loads(response.text)
        logger.info("Found %d results for %s" % (len(result['data']), domain))
        results.extend(result['data'])
        if len(results) > 249:
            logger.info("Found %d entries for %s, moving to next domain" % (len(results), domain))
            break  # don't spend too much time on one domain

    # parse through results for unique .gov.my domains/sub-domains
    domains = []
    for result in results:
        result['domains'].append(get_CN(result['subject_name']))
        for domain in result['domains']:
            ext = tldextract.extract(domain)
            if ext.suffix == 'gov.my':
                domains.append(domain)
    domains = list(set(domains))  # unique domains

    # Write to File
    with open("./output.txt", 'a') as output_file:
        for domain in domains:
            output_file.write("%s\n" % domain)

    return domains


# Logging setup
logging.basicConfig(filename='cert_log.txt',
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


# Load Facebook app_token
key = open(facebook_key_file).readline().rstrip()  # key
returned_domains = []

x = 1
for domain in domains:
    result = check_domain(domain, key)
    if result is not None:
        returned_domains.extend(result)
    x += 1
    logger.info("Done : %d of %d" % (x, len(domains)))

with open('./delta.txt', 'w') as delta_file:
    for domain in returned_domains:
        if domain not in FQDNs['FQDNs']:
            delta_file.write('%s\n' % domain)

logger.info("END")
