from custom_config import processed_url_file, hostname_file, domain_file
from functions.get_functions import get_hostname
import tldextract

# Get all the URLS
with open("../" + processed_url_file, 'r') as f:
    urls = f.readlines()

# Get all the hostnames
hostnames = [get_hostname(url.lower()) for url in urls]
domains = []
for url in urls:
    domain = tldextract.extract(url.lower()).domain + "." + \
             tldextract.extract(url.lower()).suffix
    domains.append(domain)

# write out to file
with open("../" + hostname_file, 'w') as f:
    for hostname in sorted(set(hostnames)):
        f.write(hostname + "\n")

with open('../' + domain_file, 'w') as f:
    for domain in sorted(set(domains)):
        f.write(domain + "\n")
