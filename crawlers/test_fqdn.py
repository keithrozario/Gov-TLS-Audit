import logging
import dns.resolver
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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

with open('delta.txt', 'r') as delta_file:
    new_fqdns = []
    row = 0
    for line in delta_file.readlines():
        row += 1
        try:
            answers = dns.resolver.query(line.rstrip(), 'A')
            for data in answers:
                print(data.to_text())
            logger.info('%d. ### FOUND A record for %s' % (row, line.rstrip()))
            new_fqdns.append(line.rstrip())
        except dns.resolver.NoAnswer:
            logger.info('%d. %s has no A record' % (row, line.rstrip()))
        except (dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            logger.info('%d. %s doesn\'t exist' % (row, line.rstrip()))
        except dns.exception.Timeout:
            logger.info('%d. %s was too slot to respond' % (row, line.rstrip()))

tested_fqdns = []

for fqdn in new_fqdns:
    try:
        logger.info("Testing : %s" % fqdn)
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

with open('final_list', 'w') as final_list:
    for fqdn in tested_fqdns:
        final_list.write(fqdn+"\n")
