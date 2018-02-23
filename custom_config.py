# Requests headers
chrome_UA = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
firefox_UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'
browser_UA = {'fireFox': firefox_UA, 'chrome': chrome_UA}

# Requests timeout
timeout = 5

# Successful HTTP Status Codes
http_success = [200, 203]

# output csv file
csv_file = 'output.csv'

# output json file
json_file = 'output.jsonl'
full_json_file = 'full_output.json'

# csv output
csv_data = ['hostname', 'ip', 'TLSRedirect','TLSSiteExist']
csv_cert_data = ['serialNumber', 'notValidAfter', 'signatureHashAlgorithm',\
                 'statusCode', 'statusMessage']
csv_cert_issuer = ['commonName']
csv_http_headers = ['Server', 'X-Powered-By']
csv_ip_whois = ['asn', 'asnCountryCode', 'asnDescription']

csv_header = []
csv_header.extend(csv_data)
csv_header.extend(csv_cert_data)
csv_header.extend(csv_cert_issuer)
csv_header.extend(csv_http_headers)
csv_header.extend(csv_ip_whois)

