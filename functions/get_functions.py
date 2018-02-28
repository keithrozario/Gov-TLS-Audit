import requests
import socket
import csv
import tldextract
from datetime import datetime

import shodan
from bs4 import BeautifulSoup
from html.parser import HTMLParser

from requests.packages.urllib3.exceptions import InsecureRequestWarning

from sslyze.server_connectivity import ServerConnectivityInfo, ServerConnectivityError
from sslyze.synchronous_scanner import SynchronousScanner
from sslyze.plugins.certificate_info_plugin import CertificateInfoScanCommand

import custom_config


class CustomResponse:

    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.error_message = error_message


# return hostname from a url (minus the http)
def get_hostname(site_url):
    ext = tldextract.extract(site_url)
    hostname = '.'.join(ext[:3])
    if hostname[:1] == ".":
        return hostname[1:]
    else:
        return hostname


def get_ip(hostname):
    try:
        ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        return None
    return ip


def get_site(site_url, browser, timeout=custom_config.timeout, verify=False):
    user_agent = custom_config.browser_UA[browser]
    headers = {'User-Agent': user_agent}
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    request = {"requestUrl": site_url,
               "headers": headers,
               "requestTime": datetime.now()}

    try:
        result = requests.get(site_url, headers=headers, timeout=timeout, verify=verify)
        response = result

    except requests.exceptions.ConnectTimeout:
        response = CustomResponse(-1, 'Connect Time Out')
    except requests.exceptions.ConnectionError:
        response = CustomResponse(-2, 'Connection Error')
    except requests.exceptions.ReadTimeout:
        response = CustomResponse(-3, 'Read Time Out')
    except requests.exceptions.TooManyRedirects:
        response = CustomResponse(-4, 'Too Many Redirects')
    except requests.exceptions.RequestException:
        response = CustomResponse(-5, 'Unknown Requests Error')

    return {'request': request, 'response': response}


def get_cert(site_json):

    hostname = get_hostname(site_json['hostname'])

    try:
        server_info = ServerConnectivityInfo(hostname=hostname)
        server_info.test_connectivity_to_server()
        command = CertificateInfoScanCommand()
        synchronous_scanner = SynchronousScanner()
        scan_result = synchronous_scanner.run_scan_command(server_info, command)
    except ServerConnectivityError:
        return None

    return scan_result


def get_shodan(ip_addr):

    try:
        with open(custom_config.shodan_key_file, 'r') as key_file:
            shodan_api_key = key_file.readline().rstrip()
            api = shodan.Shodan(shodan_api_key)
            host = api.host(ip_addr)
    except shodan.APIError:
        return None

    return host


def get_domain_whois(hostname):
    """ Get WHOIS for domain name. MyNIC does not publish this for .my domains
        Work in Progress.
    """
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


def get_certificate_status(cert_data):
    """Get Certificate status
    Checks the following:
    1. Certificate Matches Hostname
    2. Certificate has valid date (not_valid_before < today && not_valid_after > today)
    3. Certificate has TrustStore
    """
    cert_mismatch = {'statusCode': '-1', 'statusMessage': 'Certificate & Hostname mismatch'}
    cert_expired = {'statusCode': '-1', 'statusMessage': 'Certificate expired'}
    cert_future = {'statusCode': '-1', 'statusMessage': 'Certificate is future dated'}
    cert_no_intermediate = {'statusCode': '0',\
                            'statusMessage': 'Host did not provide intermediate certs, unable to build trust chain'}
    cert_success = {'statusCode': '1', 'statusMessage': 'Pass'}

    if getattr(cert_data, 'certificate_matches_hostname'):
        site_cert = getattr(cert_data,'certificate_chain')
        not_valid_before = getattr(site_cert[0],'not_valid_before')
        not_valid_after = getattr(site_cert[0], 'not_valid_after')

        if not_valid_after < datetime.now():
            return cert_expired
        elif not_valid_before > datetime.now():
            return cert_future
        elif getattr(cert_data, 'successful_trust_store') is None:
            return cert_no_intermediate
        else:
            return cert_success
    else:
        return cert_mismatch


def get_ip_asn(ip_addr):

    try:
        response = requests.get('https://api.iptoasn.com/v1/as/ip/' + ip_addr)
    except requests.exceptions.SSLError:
        return None
    except requests.exceptions.RequestException:
        return None

    if response.ok:
        return response.text
    else:
        return None


def get_domain(hostname):
    ext = tldextract.extract(hostname)
    return ext.domain


def get_input_fields(response):
    field_str = ''

    try:
        html_content = BeautifulSoup(response, 'html.parser')
        fields = [element['name'] for element in html_content.find_all('input')]

        for field in fields:
            if field not in custom_config.skip_fields:  # bypass all generic ASP fields
                field_str = field_str + "|" + str(field).replace(',', '')  # don't have a comma
    except KeyError:
        return ""

    return field_str


def get_site_title(response):

    try:
        html_content = BeautifulSoup(response, 'html.parser')
        site_title = html_content.title.string
        site_title = site_title.strip()
    except KeyError:
        return None
    except AttributeError:
        return None

    return site_title
