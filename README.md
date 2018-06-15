# Gov-TLS-Audit

Code for Gov-TLS-Audit available at [here](https://gov-tls-audit.sayakenahack.com)

This project was created to scan all `.gov.my` domains (and sub-domains) to check TLS Implementation, TLS Redirection (from http to https), Certificate Status (Valid, Expired, hostname mismatch..etc), and other general details about the site.

Version 2.0 includes Shodan search results (when available), the HTML title of the site, and the names of any form fields available on the root directory of the hostname.

# scan.py and crawl.py

scan.py scans hostnames from the /files/hostnames.txt file

crawl.py crawls from set number of urls, looking for all urls in the .gov.my domains to add to hostnames.

# Results

Daily scans results are available in csv, json, jsonl formats [here](https://gov-tls-audit.sayakenahack.com/files.html)

# API

API documentation is available [here](https://gov-tls-audit.sayakenahack.com/docs/index.html)

# Lambda

API is made available via Amazon API Gateway. Script for deploying this is in the lambda/ folder. This includes a serverless.yml file that deploys 'most' of the infra, including DynamoDB, Lambda and API Gateway. It doesn't deploy the Cloud Front domain or request the certificate -- yet!

# Contact

Contact me at keith [at] keithrozario [dot] com for more info.

# Help Needed

If you know of any hostnames I missed, consider making a pull request to this REPO adding the hostname to the hostnames.txt file.
