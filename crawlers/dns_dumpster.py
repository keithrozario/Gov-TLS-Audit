import time
import logging
from DNSDumpsterAPI import DNSDumpsterAPI
import random

hosts = []

# Logging setup
logging.basicConfig(filename='dnsdumpster.log',
                    filemode='w',  # file gets uploaded to S3 at end of run
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)

# Get domain names
with open("./registered_domains.txt", 'r') as domain_file:
    domains = []
    past_domain = False
    for domain in domain_file:
        if past_domain:
            domains.append(domain.strip())
        else:
            pass
        # DNS Dumpsters puts a daily limit on the number of calls per IP Address
        # Added this line here so we can split the calls between days or IP
        # Refer to last successful call of previous day, and put here.
        if domain.strip() == "penanglib.gov.my":
            past_domain = True

    logger.info("INFO: Retrieve %d domains" % len(domains))

with open("dns_dumpster.txt", "a") as output_file:
    # search each domain
    for domain in domains:
        logger.info("INFO: Retrieving results for %s" % domain)

        try:
            res = DNSDumpsterAPI(True).search(domain)
            try:
                for host in res['dns_records']['host']:
                    output_file.write("%s\n" % host)
            except TypeError:
                logger.error("ERROR: Unable to get results for %s" % domain)
        except IndexError:
            # IndexError is the typical response once the IP is rate-throttled, no point calling further domains
            logger.error("ERROR: Index Error for results for %s" % domain)
            exit(1)

        delay = random.randrange(3)
        # Random sleep to not overload the 'API'
        logger.info("INFO: Sleeping %d second(s) before next call" % delay)
        time.sleep(delay)
