import censys.base
import censys.certificates
import tldextract

with open('/Users/k31th/.secrets/censys', 'r') as censys_file:
    lines = censys_file.readlines()  # 1st line of file is the api_id, 2nd line is api_secret

censys_client = censys.certificates.CensysCertificates(api_id=lines[0].rstrip(),
                                                       api_secret=lines[1].rstrip())

fields = ["parsed.names"]

issuers = ['cPanel, Inc.', 'COMODO CA Limited', 'Let\'s Encrypt', 'Entrust, Inc.', 'GlobalSign nv-sa',
           'GeoTrust Inc.', 'VeriSign, Inc.', 'Symantec Corporation', 'Digicert Sdn. Bhd.',
           'GoDaddy.com, Inc.', 'Zimbra Collaboration Server', 'SomeOrganization',
           'StartCom Ltd.', 'CA', 'CloudFlare, Inc.', 'Elitecore']


gov_domains = []
for issuer in issuers:
    x = 0
    search_term = ('(gov.my) AND parsed.issuer.organization.raw:"%s"' % issuer)  # one term per issuer

    try:
        for cert in censys_client.search(search_term, fields=fields):
            x += 1
            for fqdn in cert['parsed.names']:
                ext = tldextract.extract(fqdn)
                if ext.suffix == 'gov.my':
                    if fqdn not in gov_domains:
                        gov_domains.append(fqdn)  # only append if it's a .gov.my, and append uniquely
            print("%d. Found : %s" % (x, cert['parsed.names']))
    except censys.base.CensysException:
        pass  # move to next api call


with open('censys_output.txt', 'w') as output_file:
    for domain in gov_domains:
        output_file.write('%s\n' % domain)
