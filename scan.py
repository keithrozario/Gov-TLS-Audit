import logging
import custom_config
import json
import csv
from datetime import datetime

from get_functions import get_cert, get_site, get_hostname, get_ip, get_ip_whois, get_certificate_status
from format_functions import format_site_data


def append_http(site_url, tls_flag=False):
    if tls_flag:
        return "https://" + site_url
    else:
        return "http://" + site_url


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


if __name__ == "__main__":

    # Logging setup
    logging.basicConfig(filename='log.txt',
                        filemode='a',
                        level=logging.DEBUG,
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')

    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    hostnames = ['1.moe.gov.my',
                 'keithrozario.com',
                 'eplan.water.gov.my',
                 'sps1.moe.gov.my',
                 'elesen.finas.gov.my',
                 'www.seriperdana.gov.my',
                 'epayment.skmm.gov.my',
                 'aduan.skmm.gov.my']

    csv_data = ['hostname', 'ip', 'TLSRedirect',\
                'TLSSiteExist']
    csv_cert_data = ['serialNumber', 'notValidAfter', 'signatureHashAlgorithm',\
                     'statusCode', 'statusMessage']

    browser = 'fireFox'
    site_datas = []
    site_datas_formatted = []

    with open('output.json', 'w') as outfile:
        pass

    with open('output.csv', 'a', newline='') as csvfile:
        pass

    with open('hostnames.txt') as f:
        hostnames = f.readlines()

    hostnames = [x.strip() for x in hostnames]

    for hostname in hostnames:

        logger.info("Hostname: " + hostname)

        site_data = dict()
        site_data['hostname'] = get_hostname(hostname)
        site_data['ip'] = get_ip(site_data['hostname'])

        if site_data['ip']:
            # IP Whois
            logger.info("Getting WHOIS for IP: " + site_data['ip'])
            site_data['ipWhois'] = get_ip_whois(site_data['ip'])

            # Request HTTP Site
            http_url = append_http(hostname, False)
            logger.info("HTTP Request: " + http_url)
            request_response = get_site(http_url, browser)
            site_data['httpRequest'] = request_response['request']
            site_data['httpResponse'] = request_response['response']

            # If http request is re-directed to https, set TLS_Redirect True and proceed
            # Else request https://hostname
            if site_data['httpResponse'].status_code in custom_config.http_success:
                if site_data['httpResponse'].history:
                    if site_data['httpResponse'].url[4] in ['S', 's']:
                        logger.info("HTTP redirected to HTTPS: " + site_data['httpResponse'].url)
                        TLS_redirect = True
                        TLS_site_exist = True
                    else:
                        TLS_redirect = False
                else:
                    TLS_redirect = False
            else:
                TLS_redirect = False

            # No TLS Redirection, try direct https://
            if not TLS_redirect:
                # Request HTTPS Site
                https_url = append_http(hostname, True)
                logger.info("No HTTPs-Redirect, making explicit HTTPs request: " + https_url)
                request_response = get_site(https_url, browser)
                site_data['httpsRequest'] = request_response['request']
                site_data['httpsResponse'] = request_response['response']
                if site_data['httpsResponse'].status_code in custom_config.http_success:
                    TLS_site_exist = True
                else:
                    TLS_site_exist = False

            # TLS Site Exist, check certs
            if TLS_site_exist:
                logger.info("HTTPs Detected. Checking Certs")
                cert_data = get_cert(site_data)
                if cert_data:
                    site_data['certData'] = cert_data
                    site_data['certStatus'] = dict()
                    site_data['certStatus'] = get_certificate_status(cert_data)
                    logger.info("Cert Data Saved")
                else:
                    logger.info("Unable to get Certificate Data")
            else:
                logger.info("HTTPs not detected. Bypassing Cert Checks")
            site_data['TLSRedirect'] = TLS_redirect
            site_data['TLSSiteExist'] = TLS_site_exist

        else:
            logger.info("Unable to Lookup IP, bypassing all checks")

        site_data_formatted = format_site_data(site_data)
        site_datas_formatted.append(site_data_formatted)
        csv_list = []

        if site_data['ip'] is None:
            csv_list.append(hostname)
            csv_list.append("Fail")
        else:
            for data in csv_data:
                csv_list.append(site_data_formatted[data])

            if 'certData' in site_data_formatted:
                for data in csv_cert_data:
                    csv_list.append(site_data_formatted['certData'][data])

        with open('output.json', 'a') as outfile:
            json.dump(site_data_formatted, outfile, cls=DateTimeEncoder)
            outfile.write("\n")

        with open('output.csv', 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',')
            csvwriter.writerow(csv_list)

    print(site_data_formatted)