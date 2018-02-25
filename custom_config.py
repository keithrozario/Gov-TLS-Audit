# Requests headers
chrome_UA = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
firefox_UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'
browser_UA = {'fireFox': firefox_UA, 'chrome': chrome_UA}

# Requests timeout
timeout = 5

# Successful HTTP Status Codes
http_success = [200, 203]

# input/output files
visited_urls_file = 'files/visited_urls.txt'
hostname_file = 'files/hostnames.txt'
csv_file = 'files/output.csv'
json_file = 'files/output.jsonl'
full_json_file = 'files/full_output.json'
processed_url_file = 'files/processed_urls.txt'

# csv output
csv_data = ['hostname', 'ip', 'TLSRedirect','TLSSiteExist']
csv_cert_data = ['serialNumber', 'notValidAfter', 'signatureHashAlgorithm',\
                 'statusCode', 'statusMessage']
csv_cert_issuer = ['commonName']
csv_http_headers = ['Server', 'X-Powered-By']
csv_ip_whois = ['asn', 'asnCountryCode', 'asnDescription']

# header of csv file
csv_header = []
csv_header.extend(csv_data)
csv_header.extend(csv_cert_data)
csv_header.extend(csv_cert_issuer)
csv_header.extend(csv_http_headers)
csv_header.extend(csv_ip_whois)

# list of domains to skip (don't crawl)
skip_domains = ['twitter', 'facebook', 'youtube', 'google', 'instagram',
                'vimeo', 'thestar', 'goo', 'feedburner', 'statcounter',
                'blogspot', 'nst', 'youtu', 'bit', 'wordpress',
                'is']

# list of file extensions to skip
skip_extensions = ['pdf', 'txt', 'xls', 'doc', 'jpg', 'png']

# start links for crawler
start_links = ['http://www.kln.gov.my/web/guest/other-ministry',
               'https://moe.gov.my/index.php/my/',
               'http://www.skmm.gov.my/',
               'http://moha.gov.my/',
               'http://mod.gov.my/',
               'http://www.selangor.gov.my/',
               'http://www.penang.gov.my']
