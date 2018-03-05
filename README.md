# Gov-TLS-Audit

Code for siteaudit.sayakenahack.com

This project was created to scan all .gov.my domains and check whether the sites deployed TLS, TLS Redirection (from http to https), Certificate Status (Valid, Expired, hostname mismatch..etc), and other general details about the site.

Version 2.0 includes Shodan search results (when available), the HTML title of the site, and the names of any form fields available on the root directory of the hostname.

# scan.py and crawl.py

scan.py scans hostnames from the /files/hostnames.txt file

crawl.py crawls from set number of urls, looking for all urls in the .gov.my domains to add to hostnames.

# Results

Results are available in the output/ folder. Results are given in JSON, JSONL and CSV formats.CSV Formats has only subset of the data, consider using the JSON or JSONL for full record set. Or use the API.

:warning: copy-pasting the csv from the RAW data on github won't work. You need to download the entire contents of the repo and get the csv from there. :warning:

# API

API is available on https://siteaudit.sayakenahack.com/api/siteDetails?FQDN=

Only one endpoint is available for now. API returns the latest scan, API data model to be published shortly. I chose to use the term FQDN (Fully Qualified Domain Name) as the parameter name, as it's more explicit than the ambigiously named 'hostname'. 

# Lambda

API is made available via Amazon API Gateway. Script for deploying this is in the lambda/ folder. This includes a serverless.yml file that deploys 'most' of the infra, including DynamoDB, Lambda and API Gateway. It doesn't deploy the Cloud Front domain or request the certificate -- yet!

# Contact

Contact me at keith [at] keithrozario [dot] com for more info.

# Help Needed

If you know of any hostnames I missed, consider making a pull request to this REPO adding the hostname to the hostnames.txt file.
