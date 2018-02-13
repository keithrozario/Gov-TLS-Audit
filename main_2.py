import logging
import json
import custom_config

from get_functions import get_cert, get_site, get_hostname, get_ip, get_ip_whois
from format_functions import format_site_data


def append_http(site_url, tls_flag=False):
    if tls_flag:
        return "https://" + site_url
    else:
        return "http://" + site_url


########################################################################################################################
#     MAIN                                                                                                             #
########################################################################################################################

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

    urls = ['eplan.water.gov.my',
            'sps1.moe.gov.my/indexsso.php',
            '1.moe.gov.my',
            # 'elesen.finas.gov.my',
            # 'www.seriperdana.gov.my/Lawatan_KSP/apply/',
            # 'epayment.skmm.gov.my',
            # 'aduan.skmm.gov.my/Complaint/AddComplaint?NOSP=1',
            'keithrozario.com']

    browser = 'fireFox'
    site_datas = []

    for url in urls:

        site_data = dict()
        site_data['hostname'] = get_hostname(url)
        site_data['url'] = url
        site_data['ip'] = get_ip(site_data['hostname'])
        logger.info("Hostname: " + site_data['hostname'])

        if site_data['ip']:
            # IP Whois
            logger.info("Getting WHOIS for IP: " + site_data['ip'])
            site_data['ipWhois'] = get_ip_whois(site_data['ip'])

            # Request HTTP Site
            http_url = append_http(url, False)
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
                https_url = append_http(url, True)
                logger.info("No Https-Redirect, making explicit https request: " + https_url)
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
                    logger.info("Cert Data Saved")
                else:
                    logger.info("Unable to get Certificate Data")
            else:
                logger.info("HTTPs not detected. Bypassing Cert Checks")
        else:
            logger.info("Unable to Lookup IP, bypassing all checks")

        site_datas.append(site_data)

    results = {'results': site_datas}
    resultsJson = json.dumps(results, default=str)
    parsed = json.loads(resultsJson)

    with open('output.txt', 'w') as outfile:
        json.dump(parsed, outfile, indent=4, sort_keys=True)

    for site_data in site_datas:
        site_data_output = format_site_data(site_data)
        print(site_data_output)