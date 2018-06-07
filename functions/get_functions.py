import requests
import socket
import tldextract
from datetime import datetime
import sslyze

import json
from bs4 import BeautifulSoup

from requests.packages.urllib3.exceptions import InsecureRequestWarning

from sslyze.server_connectivity_tester import ServerConnectivityTester, ServerConnectivityError, ServerNotReachableError
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
    # I know, I know --- but there's just so many exceptions to catch :(
    except :
        response = CustomResponse(-6, 'Unknown Error')

    return {'request': request, 'response': response}


def get_cert(site_json):

    hostname = get_hostname(site_json['hostname'])

    try:
        server_tester = ServerConnectivityTester(hostname=hostname)
        server_info = server_tester.perform()
        command = CertificateInfoScanCommand()
        synchronous_scanner = SynchronousScanner()
        scan_result = synchronous_scanner.run_scan_command(server_info, command)
    except sslyze.server_connectivity_tester.ServerNotReachableError:
        return None
    except sslyze.server_connectivity_tester.ServerConnectivityError:  # plugin has very little documentation, keeping this here for now
        return None
    except OSError:
        return None
    except RuntimeError:
        return None
    except ValueError:
        return None

    return scan_result


def get_shodan(ip_addr, api_key):

    base_url = 'https://api.shodan.io/shodan/host/'
    url = base_url + str(ip_addr)
    params = {'key': api_key}
    try:
        response = requests.get(url, params=params)
        if response.ok:
            shodan_results = json.loads(response.text)
            return shodan_results
        else:
            return None
    except requests.exceptions.SSLError:
        return None
    except requests.exceptions.RequestException:
        return None
    except:
        return None


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
    cert_no_intermediate = {'statusCode': '0',
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


def get_meta_redirect(content):

    html_content = BeautifulSoup(content, 'html.parser')

    try:
        # find meta
        refresh_header = html_content.find('meta', attrs={'http-equiv': 'refresh'})
        refresh_content = refresh_header['content']
        url = refresh_content[refresh_content.find("url=") + len("url="):]
        if url[:5] == 'https':
            TLS_Redirect = True
            redirect_type = "meta-tag"
        elif html_content.text.find("window.location.") > 0:
            TLS_Redirect = False
            redirect_type = "javascript?"
        else:
            TLS_Redirect = False
            redirect_type = "None"
    except (TypeError, IndexError):
        TLS_Redirect = False
        redirect_type = "None"

    return TLS_Redirect, redirect_type
