import json
import tldextract
from functions.get_functions import get_ip

sub_domains = []
with open("files/backup.txt","r") as file:
    for line in file:
        try:
            results = json.loads(line)
            domain = tldextract.extract(results['subdomains'][0]).registered_domain
            sub_domains.extend(results["subdomains"])
        except KeyError:
            pass

with open("files/hostnames.txt", "r") as hostnames:
    for hostname in hostnames:
        sub_domains.extend(hostname)

with open("files/hostnames_2.txt","w") as new_hostnames:
    dedup_sub_domains = list(set(sub_domains))
    dedup_sub_domains.sort()
    for domain in dedup_sub_domains:
        try:
            if get_ip(domain):
                new_hostnames.write(domain + "\n")
                print("Added %s to file" % domain)
            else:
                print("Couldn't resolve %s" % domain)
        except UnicodeError:
            pass

