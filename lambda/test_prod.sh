#!/bin/bash

echo -e "Results: 200 with body (first record 1govserv.1govnet.gov.my)\n"
sls invoke -f get_by_fqdn -p test/200_get_by_fqdn.json --stage Prod
echo -e "Results: 200 with body (last recored www2.selangor.gov.my)\n"
sls invoke -f get_by_fqdn -p test/200_get_by_fqdn_2.json --stage Prod
echo -e "Results: 200 with body (record with decimal pengundi.spr.gov.my)\n"
sls invoke -f get_by_fqdn -p test/200_get_by_fqdn_decimal.json --stage Prod
echo -e "\n\nResults: 400 with no body\n"
sls invoke -f get_by_fqdn -p test/400_get_by_fqdn.json --stage Prod
echo -e "\n\nResults: 404 with no body\n"
sls invoke -f get_by_fqdn -p test/404_get_by_fqdn.json --stage Prod
echo -e "\n\nList Scans\n"
sls invoke -f list_scans --stage Prod
echo -r "\n\nDownload Scans\n"
sls invoke -f download_zip -p test/200_download_zip.json >> output.txt --stage Prod
echo -e "\n\nCurling Rest API\n"
curl https://siteaudit.sayakenahack.com/api/siteDetails?FQDN=www2.selangor.gov.my
echo -e "\n\nCurling Rest API (non-https)\n"
curl http://siteaudit.sayakenahack.com/api/siteDetails?FQDN=1govserv.1govnet.gov.my
echo -e "\n\nCurling Rest API (decimal record)\n"
curl https://siteaudit.sayakenahack.com/api/siteDetails?FQDN=pengundi.spr.gov.my
echo -e "\n\nCurling Rest listed scans\n"
curl https://siteaudit.sayakenahack.com/api/listScans
echo -e "\n\nGetting a sample download\n"
wget https://siteaudit.sayakenahack.com/api/downloadZip?file=scan_2018-04-07.zip scan_2018-04-07.zip
echo -e "\n#####DONE####\n"
