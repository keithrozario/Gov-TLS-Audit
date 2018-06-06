import asyncio
import concurrent.futures
import time
import logging
import requests

from custom_config import start_links, http_success, skip_extensions, processed_url_file, hostname_file
from functions.get_functions import get_site, get_hostname
from bs4 import BeautifulSoup, SoupStrainer


# returns all links in a url (in a list)
def get_links(url, link_number, iteration, links_length):
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
                            # and ending with .gov.my or .mil.my
                            if get_hostname(str(link['href']))[-7:] in ['.mil.my', '.gov.my']:
                                # and does not end with file extension
                                if str(link['href'])[-3:] not in skip_extensions:
                                    links.append(link['href'])

                with open(processed_url_file, 'a') as f:
                    for link in links:
                        f.write(link + "\n")

                logger.info(str(iteration) + "-" + str(link_number) + "/" + str(links_length) +
                            ": Found " + str(len(links)) + " links in " + url)
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


async def async_get(hostnames, iter):

    loop = asyncio.get_event_loop()
    futures = [
        loop.run_in_executor(
            None,
            get_links,
            hostnames[i], i, iter, len(hostnames)
        )
        for i in range(len(hostnames))
    ]
    for response in await asyncio.gather(*futures):
        pass


async def parallel_get(hostnames, iter):

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:

        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor,
                get_links,
                hostnames[i], i, iter, len(hostnames)
            )
            for i in range(len(hostnames))
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

# empty out file, and write the initial list
with open(processed_url_file, 'w') as f:
    f.writelines(start_links)

next_links = start_links
visited_links = []

for i in range(3):

    # Code block writes all links in a page to process_url_file
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_get(next_links, i))

    visited_links.extend(next_links)

    # Open processed_url_file to get all the links processed this round
    with open(processed_url_file, 'r') as f:
        processed_urls = f.readlines()
        processed_urls = [x.strip() for x in processed_urls]

    # Deduplicate processed urls, and add unvisited to next links
    del next_links[:]
    next_links = [x for x in set(processed_urls) if x not in visited_links]

logger.info("Scan Complete, consolidating info")

# hostnames of all visited and processed urls
all_hostnames = [get_hostname(url) for url in (next_links + visited_links)]

with open(hostname_file, 'w') as f:
    for hostname in set(all_hostnames):
        f.write(hostname + "\n")

end = time.time()
print("\n\n Time Taken: " + str(end - start))