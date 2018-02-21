# Requests headers
chrome_UA = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
firefox_UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
browser_UA = {'fireFox': firefox_UA, 'chrome': chrome_UA}

# Requests timeout
timeout = 5

# Successful HTTP Status Codes
http_success = [200, 203]


# CSV File
csv_file = 'urls.csv'
csv_columns = ['url', 'Gov Dept.', 'Site Title']
csv_delimiter = ","
