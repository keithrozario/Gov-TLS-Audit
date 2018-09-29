import requests
import json
import datetime
import logging

"""
Testing of the end-point APIs
This testing script runs on the virtualenv of the main script (as it requires requests)
"""

base_url = 'https://govscan.info/api/v2/'

# Logging setup
logging.basicConfig(filename='test_results.log',
                    filemode='w',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)


def check_scanObject(scanObject):
    try:
        if scanObject['scanDate'] is not None:
            if scanObject['ip'] is not None:
                if scanObject['httpRequest']['requestTime'] is not None:
                    return True
    except KeyError:
        return False


def test_get_latest_fqdn(fqdn):

    endpoint = 'siteLatest'

    payload = {"FQDN": fqdn}
    response = requests.get(base_url + endpoint, params=payload)
    scanObject = json.loads(response.text)
    return check_scanObject(scanObject)


def test_get_latest_fqdn(fqdn, limit=None, scan_date=None):

    endpoint = 'siteHistory'
    payload = {"FQDN": fqdn}

    if limit:
        payload['limit'] = limit
    else:
        limit = 30  # default limit

    if scan_date:
        payload['scanDate'] = scan_date
        scan_date = datetime.date(int(scan_date[:4]),
                                  int(scan_date[5:7]),
                                  int(scan_date[8:]))
    else:
        scan_date = datetime.date.today() + datetime.timedelta(days=1)  # tomorrow's date

    response = requests.get(base_url + endpoint, params=payload)
    scanObjects = json.loads(response.text)
    try:
        if len(scanObjects['results']) == limit:
            if scanObjects['results'][0]['scanDate']:
                date_string = scanObjects['results'][0]['scanDate']
                object_date = datetime.date(int(date_string[:4]),
                                            int(date_string[5:7]),
                                            int(date_string[8:]))
                if scan_date > object_date:
                    if scanObjects['results'][0]['htmlSize']:
                        if scanObjects['results'][0]['TLSRedirect']:
                            return True
                else:
                    logger.info("FAIL: Scan Dates were not older than queried")
                    return False
    except KeyError:
        return False


logger.info("\nTesting Site History\n")

logger.info("Calling Site History with limit of 15")
if test_get_latest_fqdn('www.skmm.gov.my', 15):
    logger.info("PASS")
else:
    logger.info("FAIL")

logger.info("Calling Site History with no limit")
if test_get_latest_fqdn('www.skmm.gov.my'):
    logger.info("PASS")
else:
    logger.info("FAIL")

logger.info("Calling Site History with a scan_date")
if test_get_latest_fqdn('www.skmm.gov.my', scan_date='2018-08-01'):
    logger.info("PASS")
else:
    logger.info("FAIL")

logger.info("Calling Site History with a scan_date and limit")
if test_get_latest_fqdn('www.skmm.gov.my', scan_date='2018-08-01', limit=10):
    logger.info("PASS")
else:
    logger.info("FAIL")










