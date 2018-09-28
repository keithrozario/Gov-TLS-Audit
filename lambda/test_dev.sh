#!/bin/bash
APIBASEURL=https://dx5mswpa5d.execute-api.us-west-2.amazonaws.com/ProdNew/api/v2
STAGE=""
echo -e "Results: 200 with body (first record 1govserv.1govnet.gov.my)\n"
sls invoke -f get_latest_fqdn -p test/200_get_latest_fqdn.json $STAGE
echo -e "Results: 200 with body (last recored www2.selangor.gov.my)\n"
sls invoke -f get_latest_fqdn -p test/200_get_latest_fqdn_2.json $STAGE
echo -e "Results: 200 with body (record with decimal pengundi.spr.gov.my)\n"
sls invoke -f get_latest_fqdn -p test/200_get_latest_fqdn_decimal.json $STAGE
echo -e "\n\nResults: 400 with no body\n"
sls invoke -f get_latest_fqdn -p test/400_get_latest_fqdn.json $STAGE
echo -e "\n\nResults: 404 with no body\n"
sls invoke -f get_latest_fqdn -p test/404_get_latest_fqdn.json $STAGE
echo -e "\n\nList Scans\n"
sls invoke -f list_scans $STAGE
echo -e "\n\nCurling Rest API\n"
curl "$APIBASEURL/siteLatest?FQDN=www2.selangor.gov.my"
echo -e "\n\nCurling Rest API (non-https)\n"
curl "$APIBASEURL/siteLatest?FQDN=1govserv.1govnet.gov.my"
echo -e "\n\nCurling Rest API (decimal record)\n"
curl "$APIBASEURL/siteLatest?FQDN=pengundi.spr.gov.my"
echo -e "\n\nCurling Rest listed scans\n"
curl "$APIBASEURL/listScans"
echo -e "\n\nResults: 200 for 2018-04-13T01:20:01.686064\n"
sls invoke -f get_history_fqdn -p test/200_get_scan_history.json $STAGE
echo -e "Results: 200 , 20 records from today\n"
sls invoke -f get_history_fqdn -p test/200_get_scan_history_no_date.json $STAGE
echo -e "Results: 200 , 20 records from 13-04-2018\n"
sls invoke -f get_history_fqdn -p test/200_get_scan_history_no_time.json $STAGE
echo -e "\n\nCurling History for pengundi.spr.gov.my\n"
curl "$APIBASEURL/siteHistory?FQDN=pengundi.spr.gov.my"
echo -e "\n\nCurling History for www.skmm.gov.my"
curl "$APIBASEURL/siteHistory?FQDN=www.skmm.gov.my"
echo -e "\n\nCurling History for pengundi.spr.gov.my from 15-Apr"
curl "$APIBASEURL/siteHistory?FQDN=pengundi.spr.gov.my&scanDate=2018-04-16"
echo -e "\n\nCurling History for pengundi.spr.gov.my from 15-Apr (with time)"
curl "$APIBASEURL/siteHistory?FQDN=pengundi.spr.gov.my&scanDate=2018-04-15T01:20:01.686065"
echo -e "\n\nCurling History for pengundi.spr.gov.my from 15-Apr (with time), limit 1"
curl "$APIBASEURL/siteHistory?FQDN=pengundi.spr.gov.my&scanDate=2018-04-15T01:20:01.686065&limit=1"
echo -e "\n\nCurling History for pengundi.spr.gov.my from 15-Apr (with time), limit 10"
curl "$APIBASEURL/siteHistory?FQDN=pengundi.spr.gov.my&scanDate=2018-04-15T01:20:01.686065&limit=10"
echo -e "\n\nCurling History for pengundi.spr.gov.my from 15-Apr (with time), limit 10"
curl "$APIBASEURL/siteHistory?FQDN=pengundi.spr.gov.my&scanDate=2018-04-15T01:20:01.686065&limit=30"
echo -e "Results: 200 with body (scan details)\n"
sls invoke -f get_scan -p test/200_get_scan.json $STAGE
echo -e "Results: 200 with body (scan details_2)\n"
sls invoke -f get_scan -p test/200_get_scan_2.json $STAGE
echo -e "Results: 400 with body (scan details)\n"
sls invoke -f get_scan -p test/200_get_latest_fqdn.json $STAGE
echo -e "Results: 404 with body (scan details)\n"
sls invoke -f get_scan -p test/404_get_scan.json $STAGE
echo -e "Invoking API 200 (1govserv)"
curl "$APIBASEURL/scanDetails?FQDN=1govserv.1govnet.gov.my&scanDate=2018-04-16T01:20:12.674475"
echo -e "Invoking API 404 (1govserv)"
curl "$APIBASEURL/scanDetails?FQDN=1govserv.1govnet.gov.my&scanDate=2018-04-16T01:20:12.999999"
echo -e "Invoking API 200 (pengundi.gov.my)"
curl "$APIBASEURL/scanDetails?FQDN=pengundi.spr.gov.my&scanDate=2018-04-18T03:39:49.250768"
echo -e "List Hostnames"
sls invoke -f list_hostnames $STAGE
echo -e "List Hostnames"
curl "$APIBASEURL/listFQDNs"
echo -e "List domains"
sls invoke -f list_domains $STAGE
echo -e "List Hostnames"
curl "$APIBASEURL/listDNs"
echo -e "\n### Query for DNS Records###\n"
sls invoke -f query_dns_records -p test/200_query_dns.json
echo -e "\n#### Get DNS Records for spr.gov.my ###\n"
curl "$APIBASEURL/DNSRecords?DN=spr.gov.my"
echo -e "\n\nGet DNS Records for www.skmm.gov.my"
curl "$APIBASEURL/DNSRecords?DN=skmm.gov.my"


echo -e "\n#####DONE####\n"