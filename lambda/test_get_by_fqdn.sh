echo -e "Results: 200 with body (first record 1govserv.1govnet.gov.my)\n"
sls invoke -f get_by_fqdn -p test/200_get_by_fqdn.json
echo -e "Results: 200 with body (last recored www2.selangor.gov.my)\n"
sls invoke -f get_by_fqdn -p test/200_get_by_fqdn_2.json
echo -e "\n\nResults: 400 with no body\n"
sls invoke -f get_by_fqdn -p test/400_get_by_fqdn.json
echo -e "\n\nResults: 404 with no body\n"
sls invoke -f get_by_fqdn -p test/404_get_by_fqdn.json
echo -e "\n\nCurling Rest API\n"
curl https://siteaudit.sayakenahack.com/api/siteDetails?FQDN=www2.selangor.gov.my
echo -e "\n\nCurling Rest API (non-https)\n"
curl http://siteaudit.sayakenahack.com/api/siteDetails?FQDN=1govserv.1govnet.gov.my