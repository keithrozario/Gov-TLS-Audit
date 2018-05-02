import logging
import json
import csv
from datetime import datetime
from custom_config import http_success
from custom_config import csv_file, json_file, full_json_file, csv_header, hostname_file

from functions.get_functions import get_hostname, get_domain
from functions.get_functions import get_site, get_input_fields, get_site_title, get_meta_redirect
from functions.get_functions import get_ip, get_ip_asn
from functions.get_functions import get_cert, get_certificate_status
from functions.get_functions import get_shodan
from functions.format_functions import format_json_data, format_csv_data


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
    logging.basicConfig(filename='logs/scan.log',
                        filemode='w',  # file gets uploaded to S3 at end of run
                        level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')

    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    browser = 'fireFox'
    site_data_json = []
    site_jsons = []

    with open(json_file, 'w') as dumb_file:
        pass

    with open(csv_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(csv_header)

    with open(hostname_file) as f:
         hostnames = f.readlines()

    hostnames = [x.strip() for x in hostnames]

    for hostname in hostnames:

        logger.info("\nHostname: " + hostname)

        site_data = dict()
        site_data_json = dict()
        csv_list = []

        site_data['hostname'] = get_hostname(hostname)
        site_data['FQDN'] = get_hostname(hostname)
        site_data['domain'] = get_domain(hostname)
        site_data['ip'] = get_ip(site_data['hostname'])
        site_data['scanDate'] = datetime.now()

        if site_data['ip'] and site_data['ip'][:3] != '10.':

            # Request HTTP Site
            http_url = append_http(hostname, False)
            logger.info("INFO: HTTP Request: " + http_url)
            request_response = get_site(http_url, browser)
            site_data['httpRequest'] = request_response['request']
            site_data['httpResponse'] = request_response['response']

            # Check response
            if site_data['httpResponse'].status_code not in http_success:
                logger.info("ERROR: HTTP request failed status code=" +
                            str(site_data['httpResponse'].status_code))
                continue  # go to next site
            else:

                # Shodan Scan
                logger.info("INFO: Calling Shodan for : " + site_data['ip'])
                shodan_results = get_shodan(site_data['ip'])
                if shodan_results:
                    site_data['shodan'] = shodan_results
                else:
                    logger.info("WARNING: No Shodan Results for IP")

                # ASN Info
                asn_info = get_ip_asn(site_data['ip'])
                if asn_info:
                    site_data['asnInfo'] = asn_info

                # Http request successful check for form Fields
                form_fields = get_input_fields(site_data['httpResponse'].content)
                if form_fields:
                    site_data['formFields'] = form_fields

                # Http request successful check for form Fields
                site_title = get_site_title(site_data['httpResponse'].content)
                if site_title:
                    site_data['siteTitle'] = site_title

                # Check if re-directed to https, set TLS_Redirect
                if site_data['httpResponse'].history:
                    if site_data['httpResponse'].url[4] in ['S', 's']:
                        logger.info("GOOD: Redirect to HTTPS: " + site_data['httpResponse'].url)
                        TLS_redirect = True
                        TLS_site_exist = True
                    else:
                        TLS_redirect = False
                else:
                    TLS_redirect = False

            # No TLS Redirection, try direct https://
            if not TLS_redirect:

                # Request HTTPS Site
                https_url = append_http(hostname, True)
                logger.info("INFO: No HTTPs-Redirect, making explicit HTTPs request: " + https_url)
                request_response = get_site(https_url, browser)
                site_data['httpsRequest'] = request_response['request']
                site_data['httpsResponse'] = request_response['response']
                if site_data['httpsResponse'].status_code in http_success:
                    TLS_site_exist = True
                else:
                    TLS_site_exist = False

            # Last bit of javascript checks
            if TLS_redirect:
                site_data['TLSRedirect'] = TLS_redirect
                site_data['redirectType'] = "HTTP Status Code"
            elif TLS_site_exist:
                # TLS Redirect is False, but https site exist, check meta tag
                site_data['TLSRedirect'], site_data['redirectType'] = get_meta_redirect(site_data['httpResponse'].content)
            else:
                site_data['TLSRedirect'] = TLS_redirect
                site_data['redirectType'] = "None"

            site_data['TLSSiteExist'] = TLS_site_exist

            # TLS Site Exist, check certs
            if TLS_site_exist:
                logger.info("INFO: HTTPs Detected. Checking Certs")
                cert_data = get_cert(site_data)
                if cert_data:
                    site_data['certData'] = cert_data
                    site_data['certStatus'] = dict()
                    site_data['certStatus'] = get_certificate_status(cert_data)
                    logger.info("INFO: Cert Data Saved")
                else:
                    logger.info("ERROR: Unable to get Certificate Data")
            else:
                logger.info("INFO: HTTPs not detected. Bypassing Cert Checks")

            # Write all this to file
            site_data_json = format_json_data(site_data)
            site_jsons.append(site_data_json)
            csv_list = format_csv_data(site_data_json)

            # Write to CSV only if IP
            with open(csv_file, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile,
                                        delimiter=',',
                                        quotechar='"',
                                        quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(csv_list)

            # Write to JSONs (even it's just IP)
            with open(json_file, 'a') as outfile:
                if len(site_data_json) > 0:
                    json.dump(site_data_json, outfile, cls=DateTimeEncoder)
                    outfile.write("\n")
                else:
                    pass  # empty row

        else:
            logger.info("ERROR: No IP Found")

    # stuff below this line might not work
    full_json = {'results': site_jsons}

    with open(full_json_file, 'w') as outfile:
        json.dump(full_json, outfile, cls=DateTimeEncoder)
        outfile.write("\n")