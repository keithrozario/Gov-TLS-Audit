import asyncio
import concurrent.futures
import time
import logging
import requests

from custom_config import hostname_file, http_success, skip_extensions, processed_url_file
from get_functions import get_site, get_hostname
from bs4 import BeautifulSoup, SoupStrainer


# returns all links in a url (in a list)
def get_links(url):
    links = []

    try:

        request_response = get_site(url, 'fireFox')
        if request_response['response'].status_code in http_success:
            html_content = request_response['response'].content
            try:

                for link in BeautifulSoup(html_content, 'html.parser', parse_only=SoupStrainer('a')):
                    if link.has_attr('href'):
                        # skip internal links, check only for links with http
                        if str(link['href'])[:4] == 'http':
                            # and ending with .gov.my
                            if get_hostname(str(link['href']))[-7:] == ".gov.my":
                                # and does not end with file extension
                                if str(link['href'])[-3:] not in skip_extensions:
                                    links.append(link['href'])

                with open(processed_url_file, 'a') as f:
                    for link in links:
                        f.write(link + "\n")

                logger.info("GOOD: Found " + str(len(links)) + " links in " + url)
            except NotImplementedError:
                logger.error("BAD: Unable to parse file")

        else:
            logger.error("Error HTTP Status:" + str(request_response['response'].status_code) +
                         "," + url)
    except requests.exceptions.ChunkedEncodingError:
        logger.error("\n##### Chunked Encoding Error on:" + url)
    except requests.exceptions.Timeout:
        logger.error("\n##### Timeout error on:" + url)
    except requests.exceptions.ConnectionError:
        logger.error("\n##### Connection Error on:" + url)
    except requests.exceptions.RequestException:
        logger.error("\n##### Unknown Requests Error on:")
    # except:
    #    logger.error("\n##### Unknown Error :" + url)

    return links


async def parallel_get(hostnames):

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:

        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor,
                get_links,
                hostname
            )
            for hostname in hostnames
        ]
        for response in await asyncio.gather(*futures):
            pass

start = time.time()

# Logging setup
logging.basicConfig(filename='logs/crawl.log',
                    filemode='a',
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)

start_links = []

start_links.append('http://www.kln.gov.my/web/guest/other-ministry')
start_links.append('https://moe.gov.my/index.php/my/')
start_links.append('http://moh.gov.my/')
start_links.append('http://www.skmm.gov.my/')
start_links.append('http://moha.gov.my/')
start_links.append('http://mod.gov.my/')
start_links.append('http://www.selangor.gov.my/')
start_links.append('http://www.penang.gov.my')
start_links.append('http://sabah.gov.my')
start_links.append('http://www.melaka.gov.my')


# with open(hostname_file) as f:
#     hostnames = f.readlines()
#
# hostnames = [x.strip() for x in hostnames]

loop = asyncio.get_event_loop()
loop.run_until_complete(parallel_get(start_links))
end = time.time()
print("\n\n Time Taken: " + str(end - start))
