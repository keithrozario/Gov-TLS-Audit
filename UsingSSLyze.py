import requests
import logging
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from sslyze.server_connectivity import ServerConnectivityInfo, ServerConnectivityError
from sslyze.synchronous_scanner import SynchronousScanner
from sslyze.plugins.certificate_info_plugin import CertificateInfoScanCommand
from ssl import CertificateError


# Requests headers
chrome_UA = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
firefox_UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'

browser_UA = {'fireFox': firefox_UA, 'chrome': chrome_UA}
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Logging setup
logging.basicConfig(filename='log.txt',
                    filemode='a',
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


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


def append_http(site_url, tls_flag=False):
    if tls_flag:
        return "https://" + site_url
    else:
        return "http://" + site_url


def format_request(site_url, headers):
    return {"requestUrl": site_url,
            'headers': headers,
            "requestTime": str(datetime.now())}


def format_response(result):
    history_elapsed = 0
    response = dict()

    response["statusCode"] = result.status_code

    if result.status_code in [200, 203]:
        response["contentSize"] = len(result.content)

        if result.history:
            response["redirectCount"] = len(result.history)
            response["redirectUrl"] = result.url

            if result.url[4] in ['S', 's']:
                response["redirectHttps"] = True
            else:
                response["redirectHttps"] = False

            for history in result.history:
                history_elapsed = history_elapsed + history.elapsed.microseconds

        else:
            response["redirectHttps"] = False

        response["responseTime"] = result.elapsed.microseconds + history_elapsed

        for header_field in result.headers._store.items():
            response[header_field[1][0]] = header_field[1][1]

    return response


def request_site(site_url, http_headers, timeout=2, verify=False):

    try:
        result = requests.get(site_url, headers=http_headers, timeout=timeout, verify=verify)
        response = format_response(result)
    except requests.exceptions.ConnectTimeout:
        response = {"statusCode": -1, "statusMsg": "Connection Time Out"}
    except requests.exceptions.ConnectionError:
        response = {"statusCode": -1, "statusMsg": "Connection Error"}

    return response


def get_site(site_url, browser, timeout=2, verify=False):
    user_agent = browser_UA[browser]
    headers = {'User-Agent': user_agent}

    request = format_request(site_url, headers)
    response = request_site(site_url, headers, timeout, verify)

    return {'request': request, 'response': response}


def get_substring(fullstring, begin, end):

    substring_start = fullstring.find(begin) + len(begin)
    substring_end = fullstring[substring_start:].find(end)
    substring = fullstring[substring_start:substring_start+substring_end]

    return substring


def parse_attribute(attribute):

    result = []
    name_begin = "name="
    name_end = ")"
    value_begin = "value='"
    value_end = "'"

    result.append(get_substring(attribute, name_begin, name_end))
    result.append(get_substring(attribute, value_begin, value_end))

    return result


def format_cert(scan_result):
    cert_data = dict()

    cert_data["tlsServerNameIndication"] = scan_result.server_info.tls_server_name_indication
    cert_data["highestSslVersionSupported"] = str(scan_result.server_info.highest_ssl_version_supported)
    cert_data["sslCipherSupported"] = scan_result.server_info.ssl_cipher_supported
    cert_data["certificateMatchesHostname"] = scan_result.certificate_matches_hostname
    cert_data["serialNumber"] = scan_result.certificate_chain[0].serial_number

    if not cert_data["certificateMatchesHostname"]:
        logger.info("Invalid Cert")

    if scan_result.successful_trust_store:
        cert_data["successfulValidation"] = True
        cert_data["trustStoreName"] = scan_result.successful_trust_store.name
    else:
        cert_data["successfulValidation"] = False

    cert_data["notValidAfter"] = scan_result.certificate_chain[0].not_valid_after
    cert_data["notValidBefore"] = scan_result.certificate_chain[0].not_valid_before
    if scan_result.certificate_chain[0].not_valid_after > datetime.now():
        cert_data["certExpired"] = True
    else:
        cert_data["certExpired"] = False

    cert_data["chainLength"] = len(scan_result.certificate_chain)

    cert_data["issuerAttributes"] = dict()
    for attribute in scan_result.certificate_chain[0].issuer._attributes:
        key_value = parse_attribute(str(attribute))
        cert_data["issuerAttributes"][key_value[0]] = key_value[1]

    # for extension in scan_result.certificate_chain[0].extensions._extensions:
    #    print(parse_attribute(str(extension)))

    print("hello")


def request_cert(site_json):

    hostname = get_hostname(site_json['hostname'])

    server_info = ServerConnectivityInfo(hostname=hostname)
    server_info.test_connectivity_to_server()
    command = CertificateInfoScanCommand()
    synchronous_scanner = SynchronousScanner()

    scan_result = synchronous_scanner.run_scan_command(server_info, command)
    format_cert(scan_result)

    print("hello")


########################################################################################################################
#     MAIN                                                                                                             #
########################################################################################################################


if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    urls = ['keithrozario.com',
            'eplan.water.gov.my',
            'sps1.moe.gov.my/indexsso.php',
            '1.moe.gov.my',
            'elesen.finas.gov.my',
            'www.seriperdana.gov.my/Lawatan_KSP/apply/',
            'epayment.skmm.gov.my',
            'aduan.skmm.gov.my/Complaint/AddComplaint?NOSP=1']

    browser = 'fireFox'

    for url in urls:
        site_data = {'hostname': get_hostname(url)}

        http_url = append_http(url, False)
        request_response = get_site(http_url, browser)

        site_data['httpRequest'] = request_response['request']
        site_data['httpResponse'] = request_response['response']

        if 'redirectHttps' in site_data['httpResponse']:
            if not site_data['httpResponse']['redirectHttps']:

                https_url = append_http(url, True)
                request_response = get_site(https_url, browser)

                site_data['httpsRequest'] = request_response['request']
                site_data['httpsResponse'] = request_response['response']

        TLS = False
        if site_data['httpResponse']['statusCode'] in [200, 203]:
            if site_data['httpResponse']['redirectHttps']:
                TLS = True
            elif site_data['httpsResponse']['statusCode'] in [200, 203]:
                TLS = True

        if TLS:
            request_cert(site_data)
        else:
            logger.info("Not Requesting Certificate")
        # print(site_data)
