import requests
import json
import dns.resolver
import logging

# Logging setup
logging.basicConfig(filename='test_fqdn_log.txt',
                    filemode='a',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)

result = requests.get('https://govscan.info/api/v2/listFQDNs')
FQDNs = json.loads(result.text)['FQDNs']

with open('censys_output.txt' , 'r') as censys_file:
    censys_domains = censys_file.readlines()
    delta_domains = []
    for fqdn in censys_domains:
        if fqdn.rstrip() not in FQDNs:
            delta_domains.append(fqdn.rstrip())

with open ('facebook_delta_working.txt', 'r') as facebook_file:
    domains = facebook_file.readlines()
    active_domains = []
    x = 0
    for fqdn in delta_domains:
        x += 1
        if fqdn in domains:
            pass  # no need to rescan
        else:
            try:
                answers = dns.resolver.query(fqdn.rstrip(), 'A')
                for data in answers:
                    print(data.to_text())
                active_domains.append(fqdn)
            except dns.resolver.NoAnswer:
                logger.info('%d. %s has no A record' % (x, fqdn))
            except (dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
                logger.info('%d. %s doesn\'t exist' % (x, fqdn))
            except dns.exception.Timeout:
                logger.info('%d. %s was too slot to respond' % (x, fqdn))

tested_fqdns = []
x= 0
for fqdn in active_domains:
    try:
        x += 1
        logger.info("%d of %d Testing : %s" % (x, len(active_domains), fqdn))
        response = requests.get("http://" + fqdn, timeout=5, verify=False)
        tested_fqdns.append(fqdn)
        logger.info('Successful: %s' % fqdn)
    except requests.exceptions.ConnectTimeout:
        pass
    except requests.exceptions.ConnectionError:
        pass
    except requests.exceptions.ReadTimeout:
        pass
    except requests.exceptions.TooManyRedirects:
        pass
    except requests.exceptions.RequestException:
        pass
    # I know, I know --- but there's just so many exceptions to catch :(
    except :
        pass

with open('tested.txt', 'w') as output_file:
    for fqdn in tested_fqdns:
        output_file.write(fqdn + '\n')
