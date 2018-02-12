import requests
import ipwhois
import socket
import csv
from datetime import datetime

from requests.packages.urllib3.exceptions import InsecureRequestWarning

from sslyze.server_connectivity import ServerConnectivityInfo, ServerConnectivityError
from sslyze.synchronous_scanner import SynchronousScanner
from sslyze.plugins.certificate_info_plugin import CertificateInfoScanCommand

import custom_config


class CustomResponse:

    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.error_message = error_message


def get_hostname(site_url):

    doublequote = site_url.find("//")
    if doublequote == -1:
        hostname_start = 0
    else:
        hostname_start = doublequote + 2

    if site_url.find("/", hostname_start) == -1:
        return site_url[hostname_start:]
    else:
        hostname_end = site_url.find("/", hostname_start)
        return site_url[hostname_start:hostname_end]


def get_ip(hostname):
    try:
        ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        return None
    return ip


def get_site(site_url, browser, timeout=5, verify=False):
    user_agent = custom_config.browser_UA[browser]
    headers = {'User-Agent': user_agent}
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    request = {"requestUrl": site_url,
               "headers": headers,
               "requestTime": str(datetime.now())}

    try:
        result = requests.get(site_url, headers=headers, timeout=timeout, verify=verify)
        response = result

    except requests.exceptions.ConnectTimeout:
        response = CustomResponse(-1, 'Connect Time Out')
    except requests.exceptions.ConnectionError:
        response = CustomResponse(-2, 'Connection Error')
    except requests.exceptions.ReadTimeout:
        response = CustomResponse(-3, 'Read Time Out')

    return {'request': request, 'response': response}


def get_cert(site_json):

    hostname = get_hostname(site_json['hostname'])

    try:
        server_info = ServerConnectivityInfo(hostname=hostname)
        server_info.test_connectivity_to_server()
        command = CertificateInfoScanCommand()
        synchronous_scanner = SynchronousScanner()
    except ServerConnectivityError:
        return None

    scan_result = synchronous_scanner.run_scan_command(server_info, command)
    return scan_result


def get_ip_whois(ip_addr):

    obj = ipwhois.IPWhois(ip_addr)
    result = obj.lookup_rdap(depth=1)
    return result


def get_domain_whois(hostname):
    ''' Get WHOIS for domain name. MyNIC does not publish this for .my domains
        Work in Progress.
    '''
    # try:
    #     domain_result = whois.whois(domain)
    #     domain_data = format_whois_domain(domain_result)
    # except TypeError:
    #     domain_data = None
    #
    # return domain_data
    return None


def get_urls(filename):
    urls = []

    with open(filename, 'r', newline='', errors='ignore', encoding="utf8") as csvfile:
        readerDict = csv.DictReader(csvfile,
                                    fieldnames=custom_config.csv_columns,
                                    delimiter=custom_config.csv_delimiter)
        for row in readerDict:
            if row['url'] != 'URL':
                urls.append(row['url'])

    return urls
