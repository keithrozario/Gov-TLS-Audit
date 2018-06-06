import requests
import tldextract
import logging
import time

if __name__ == "__main__":

    # Logging setup
    logging.basicConfig(filename='logs/virus_total.log',
                        filemode='w',  # file gets uploaded to S3 at end of run
                        level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')

    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    virus_total = "/home/l33t/.virustotal/key.txt"
    base_url = "https://www.virustotal.com/vtapi/v2/domain/report"

    with open(virus_total, 'r') as key_file:
        api_key = key_file.readline().rstrip()

    with open("files/hostnames.txt") as hostname_file:
        domains = []
        for hostname in hostname_file:
            domain = tldextract.extract(hostname).registered_domain
            domains.append(domain)
        # Deduplicate domain
        dedup_domains = list(set(domains))

    with open("files/virus_total.txt", "w") as virus_total_file:
        domain_count = 0
        for domain in dedup_domains:
            # Query API
            logger.info("Requesting for: " + domain)
            params = {'apikey': api_key, 'domain': domain}
            response = requests.get(base_url, params=params)

            # Write to File
            virus_total_file.write(response.text)
            virus_total_file.write("\n")

            # Increment count and wait (4 request per minute rate limited API)
            domain_count += 1
            if domain_count % 4 == 0:
                logger.info("Requested 4 domains, pausing for 1 minute")
                time.sleep(60)

            # Wait 16 seconds
            logger.info("Done")
