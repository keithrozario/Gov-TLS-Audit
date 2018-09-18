# Requests headers
chrome_UA = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
firefox_UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'
browser_UA = {'fireFox': firefox_UA, 'chrome': chrome_UA}

# Requests timeout
timeout = 3

# Successful HTTP Status Codes
http_success = [200, 203]

# input/output files
visited_urls_file = 'files/visited_urls.txt'
hostname_file = 'files/hostnames.txt'
domain_file = 'files/domains.txt'
csv_file = 'output/output.csv'
json_file = 'output/output.jsonl'
full_json_file = 'output/full_output.json'
processed_url_file = 'files/processed_urls.txt'

# csv output
csv_data = ['domain', 'hostname', 'ip', 'TLSRedirect', 'redirectType', 'TLSSiteExist']
csv_cert_data = ['serialNumber', 'notValidBefore', 'notValidAfter',
                 'signatureHashAlgorithm', 'statusCode', 'statusMessage']
csv_cert_issuer = ['commonName']
csv_http_headers = ['Server', 'X-Powered-By']
csv_optional = ['formFields', 'siteTitle']
csv_ip = ['asn', 'asnCountryCode', 'isp']
csv_shodan =['ports', 'lastUpdate']

# header of csv file
csv_header = []
csv_header.extend(csv_data)
csv_header.extend(csv_cert_data)
csv_header.extend(['issuerCommonName'])  # renamed to something more meaningful
csv_header.extend(csv_http_headers)
csv_header.extend(csv_ip)
csv_header.extend(csv_optional)
csv_header.extend(['shodan_ports','shodan_last_update'])
csv_header.extend(['html_size'])

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

# Shodan Key File
shodan_key_file = "/home/l33t/.shodan/key.txt"
facebook_key_file = '/Users/k31th/.facebook/app_token'  # from my mac -- hence the location

# Form fields to skip (not present in csv)
skip_fields = ['__EVENTTARGET', '__EVENTARGUMENT', '__LASTFOCUS','__VIEWSTATE',
               '__VIEWSTATEGENERATOR','__PREVIOUSPAGE','__EVENTVALIDATION',
               '__VIEWSTATEENCRYPTED', '__REQUESTDIGEST']

# aws configuration
bucket_name = 'files.siteaudit.sayakenahack.com'
obj_prefix = 'scan_'
output_dir = 'output/'
dynamo_table_name = 'siteAuditGovMy'
dynamo_table_backup_prefix = 'backup_'
dynamo_table_write_capacity = 50  # write capacity during write (falls back to 0 after load)
aws_region = 'us-west-2'
endpoint_url = 'https://dynamodb.' + aws_region + '.amazonaws.com'
s3_upload_dir = "files"  # directory of bucket to upload file into
