# Gov-TLS-Audit (GovScan.info)

Site is available [here](https://govscan.info)

Project was created to scan all `.gov.my` domains (and sub-domains) to check TLS Implementation, TLS Redirection (from http to https), Certificate Status (Valid, Expired, hostname mismatch..etc), and other general details about the site.

Version 2.0 includes Shodan search results (when available), the HTML title of the site, and the names of any form fields available on the root directory of the hostname.

# scan.py

scan.py scans hostnames from this [repo](https://github.com/keithrozario/list_gov.my_websites). Consider making a pull request if you know of a `gov.my` domain that isn't being scanned. Latest version of scan.py **only** works with Python3.6 and above.

# crawlers

The `/crawlers` folder has a list of miscellaneous scripts that query OSINT databases for hostnames, subdomains, etc.


# Results

Daily scans results are available in csv, json, jsonl formats [here](https://govscan.info/files.html)

# API

API documentation is available [here](https://govscan.info/docs/index.html)

# Lambda

API is made available via Amazon API Gateway. Script for deploying this is in the lambda/ folder. This includes a serverless.yml file that deploys 'most' of the infra, including DynamoDB, Lambda and API Gateway. It doesn't deploy the Cloud Front domain or request the certificate -- yet!

# Contact

Contact me at keith [at] keithrozario [dot] com for more info.

# Help Needed

If you know of any hostnames I missed, consider making a pull request to this REPO adding the hostname to the hostnames.txt file.
