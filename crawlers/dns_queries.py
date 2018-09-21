import dns.resolver
import tldextract
import json
import requests
import logging


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

ids = ['SOA','TXT','MX','NS']

for domain in domains:
    try:
        for record_type in ids:
            try:
                answers = dns.resolver.query(domain, record_type)
                for data in answers:
                    print(domain, '-', record_type, ':', data.to_text())
            except dns.resolver.NoAnswer:
                print(domain, '-', record_type, ':', 'No answer')
            except dns.resolver.NoNameservers:
                print(domain, '-', record_type, ':', 'No Name Servers')
            except dns.exception.Timeout:
                print(domain, '-', record_type, ':', 'Timeout')
    except dns.resolver.NXDOMAIN:
        print(domain, '-', record_type, ':', 'None of the DNS Query Name exists')

