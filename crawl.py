import requests
import logging

from bs4 import BeautifulSoup, SoupStrainer
from get_functions import get_hostname, get_site
from custom_config import visited_urls_file, hostname_file, processed_url_file
from custom_config import skip_extensions, http_success

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


if __name__ == "__main__":
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

    with open(processed_url_file, 'w') as f:
        for ahref in start_links:
            f.write(ahref + "\n")

    next_links = []
    page_links = []
    visited_links = []

    next_links = start_links

    for x in range(3):

        count = 0
        for link in next_links:
            count += 1
            # Only Crawl .gov.my links
            if get_hostname(link)[-7:] == ".gov.my":
                logger.info("Iter: " + str(x) + ",link: " + str(count) + " of " + str(len(next_links)))

                # save all links to file, by default only .gov.my links are returned from get_links
                ahrefs = get_links(link)
                with open(processed_url_file, 'a') as f:
                    for ahref in ahrefs:
                        f.write(ahref + "\n")

                # add all links to page_links list (it has all the links in this iteration)
                page_links.extend(ahrefs)

                # mark link as visited
                visited_links.append(link)
            else:
                logger.info("Iter: " + str(x) + ", Non gov.my site, bypass")

        # remove duplicate in next_links
        page_links_dedup = set(page_links)
        # next_links are all links in page_links_dedup that are not in visited links
        del next_links[:]
        next_links = [x for x in page_links_dedup if x not in visited_links]

    visited_links.extend(next_links)

    with open(visited_urls_file, 'w') as f:
        for link in visited_links:
            f.write(link + "\n")

    hostnames = []
    for link in visited_links:
        hostnames.append(get_hostname(link))

    # unique hostnames
    hostnames_dedup = set(hostnames)

    with open(hostname_file, 'w') as f:
        for hostname in hostnames_dedup:
            f.write(hostname + "\n")

    logger.info(len(hostnames_dedup))
