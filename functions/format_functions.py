from custom_config import csv_data, csv_cert_data, csv_cert_issuer, csv_http_headers, csv_header, csv_ip
from custom_config import csv_optional, csv_shodan
import json
from custom_config import http_success


def copy_over(source_dict, destination_dict, source_field, destination_field, field_type='keyValue'):
    """
    appends a value from source_dict to destination_dict
    checks for existence of field/attribute before copying
    returns full destination_dict with appended field (if exist)
    returns full destination_dict without appended field (if does not exist)
    """

    if field_type == 'keyValue':
        if source_field in source_dict:
            destination_dict[destination_field] = source_dict[source_field]
        else:
            pass
    elif field_type == 'attribute':
        if hasattr(source_dict, source_field):
            destination_dict[destination_field] = getattr(source_dict, source_field)
        else:
            pass
    else:
        pass

    return destination_dict


def get_substring(full_string, begin, end):
    """ Used in parse_attribute
    """
    substring_start = full_string.find(begin) + len(begin)
    substring_end = full_string[substring_start:].find(end)
    substring = full_string[substring_start:substring_start+substring_end]

    return substring


def parse_attribute(attribute):
    """
    parses attributes in issuer, extensions and subject fields
    """
    result = []

    name_begin = "name="
    name_end = ")"
    result.append(get_substring(attribute, name_begin, name_end))

    # can be value=' or value=" , especially for let's encrypt cert
    value_begin = "value="
    value_end = ")"
    # remove the first and last character of string which will be ' or "
    result.append(get_substring(attribute, value_begin, value_end)[1:-1])

    return result


def format_json_data(site_data):

    result = dict()
    request_dicts = ['httpRequest', 'httpsRequest']
    response_dicts = ['httpResponse', 'httpsResponse']
    certData_dict = 'certData'
    certStatus_dict = 'certStatus'
    tls_server_info_dict = 'TLSServerInfo'
    shodan_dict = 'shodan'
    asn_info_dict = 'asnInfo'

    # mapping from site_data
    mapping = [['hostname', 'hostname', 'keyValue'],
               ['ip', 'ip', 'keyValue'],
               ['url', 'url', 'keyValue'],
               ['TLSRedirect', 'TLSRedirect', 'keyValue'],
               ['TLSSiteExist', 'TLSSiteExist', 'keyValue'],
               ['domain', 'domain', 'keyValue'],
               ['formFields', 'formFields', 'keyValue'],
               ['siteTitle', 'siteTitle', 'keyValue']]

    # mapping from request (http & https)
    mapping_request = [['headers','headers','keyValue'],
                       ['requestTime', 'requestTime', 'keyValue'],
                       ['requestUrl', 'requestUrl', 'keyValue']]

    # mapping from response (http & https)
    mapping_response = [['status_code', 'statusCode', 'attribute'],
                        ['url', 'url', 'attribute']]

    # mapping from certData
    mapping_cert_data = [['certificate_matches_hostname', 'certMatchesHostname', 'attribute']]

    # mapping from certStatus
    mapping_cert_status = [['statusCode', 'statusCode', 'keyValue'],
                           ['statusMessage', 'statusMessage', 'keyValue']]

    # mapping from certData['certificate_chain[0]
    mapping_cert_0 = [['not_valid_after', 'notValidAfter', 'attribute'],
                      ['not_valid_before', 'notValidBefore', 'attribute'],
                      ['serial_number', 'serialNumber', 'attribute']]

    # mapping from certData['server_info']
    mapping_server_info = [['highest_ssl_version_supported', 'highestTLSVersionSupported', 'attribute'],
                           ['ssl_cipher_supported', 'TLSCipherSupported', 'attribute'],
                           ['hostname', 'hostname', 'attribute'],
                           ['tls_server_name_indication', 'TLSServerNameIndication', 'attribute']]

    # mapping from shodan, must start with asn, country_code and isp
    mapping_shodan = [['asn', 'asn', 'keyValue'],
                      ['country_code', 'asnCountryCode', 'keyValue'],
                      ['isp', 'isp', 'keyValue'],
                      ['os','os','keyValue'],
                      ['ip_str','ipStr','keyValue'],
                      ['ports', 'ports', 'keyValue'],
                      ['last_update','lastUpdate','keyValue']]

    # mapping for asn_info
    # None

    # implement mapping for site_data
    for map_rule in mapping:
        result = copy_over(site_data, result, map_rule[0], map_rule[1], map_rule[2])

    # mapping from request
    for request_dict in request_dicts:
        if request_dict in site_data:
            result[request_dict] = dict()
            for map_rule in mapping_request:
                result[request_dict] = copy_over(site_data[request_dict], result[request_dict],
                                                 map_rule[0], map_rule[1], map_rule[2])
    # mapping from response
    for response_dict in response_dicts:
        if response_dict in site_data:
            result[response_dict] = dict()
            for map_rule in mapping_response:
                result[response_dict] = copy_over(site_data[response_dict], result[response_dict],
                                                 map_rule[0], map_rule[1], map_rule[2])

            if hasattr(site_data[response_dict], 'headers'):
                if hasattr(site_data[response_dict].headers, '_store'):
                    result[response_dict]['headers'] = {}
                    for header_field in site_data[response_dict].headers._store.items():
                        result[response_dict]['headers'][header_field[1][0]] = header_field[1][1]

            if hasattr(site_data[response_dict], 'content'):
                result[response_dict]['htmlSize'] = len(site_data[response_dict].content)

    if 'certData' in site_data:
        result[certData_dict] = dict()

        for map_rule in mapping_cert_data:
            result[certData_dict] = copy_over(site_data[certData_dict], result[certData_dict],
                                              map_rule[0], map_rule[1], map_rule[2])

        for map_rule in mapping_cert_status:
            result[certData_dict] = copy_over(site_data[certStatus_dict], result[certData_dict],
                                              map_rule[0], map_rule[1], map_rule[2])

        # certificate_chain[0]
        if hasattr(site_data['certData'], 'certificate_chain'):
            cert_chain = getattr(site_data[certData_dict], 'certificate_chain')
            for map_rule in mapping_cert_0:
                result[certData_dict] = copy_over(cert_chain[0], result[certData_dict],
                                                  map_rule[0], map_rule[1], map_rule[2])

            # signature hash algorithm
            if hasattr(cert_chain[0], 'signature_hash_algorithm'):
                result[certData_dict] = copy_over(cert_chain[0].signature_hash_algorithm, result[certData_dict],
                                                  'name','signatureHashAlgorithm', 'attribute')
            # issuer
            if hasattr(cert_chain[0], 'issuer'):
                result[certData_dict]['issuer'] = dict()
                for attribute in site_data['certData'].certificate_chain[0].issuer._attributes:
                    key_value = parse_attribute(str(attribute))
                    result[certData_dict]['issuer'][key_value[0]] = key_value[1]

            # subject
            if hasattr(cert_chain[0], 'subject'):
                result[certData_dict]['subject'] = dict()
                for attribute in site_data['certData'].certificate_chain[0].subject._attributes:
                    key_value = parse_attribute(str(attribute))
                    result[certData_dict]['subject'][key_value[0]] = key_value[1]

        # server_info
        if hasattr(site_data['certData'], 'server_info'):
            result[tls_server_info_dict] = dict()
            server_info = getattr(site_data[certData_dict], 'server_info')
            for map_rule in mapping_server_info:
                result[tls_server_info_dict] = copy_over(server_info, result[tls_server_info_dict],
                                                map_rule[0], map_rule[1], map_rule[2])

    if 'shodan' in site_data:
        result[shodan_dict] = dict()
        for map_rule in mapping_shodan:
            result[shodan_dict] = copy_over(site_data['shodan'], result[shodan_dict],
                                            map_rule[0], map_rule[1], map_rule[2])
    if 'asnInfo' in site_data:
        result[asn_info_dict] = dict()
        json_data = json.loads(site_data['asnInfo'])
        if 'as_number' in json_data:
            result['asnInfo']['asnCountryCode'] = str(json_data['as_country_code'])
            result['asnInfo']['isp'] = str(json_data['as_description'])
            result['asnInfo']['asn'] = ("AS" + str(json_data['as_number']))

    return result


def format_csv_data(site_data_json):

    result = []

    if site_data_json['ip'] is None:

        result.append(site_data_json['hostname'])

        # Append Fail and end the row
        # (header-1) because Fail i one new row
        result.extend(['' for i in range(len(csv_header)-1)])
        return result

    else:
        for data in csv_data:
            result.append(site_data_json[data])

    if 'certData' in site_data_json:
        for data in csv_cert_data:
            result.append(site_data_json['certData'][data])

        if 'issuer' in site_data_json['certData']:
            for data in csv_cert_issuer:
                result.append(site_data_json['certData']['issuer'][data])
        else:
            for c in range(len(csv_cert_issuer)):
                result.append('')
    else:
        for c in range(len(csv_cert_data)+len(csv_cert_issuer)):
            result.append('')

    if 'httpResponse' in site_data_json:
        if 'headers' in site_data_json['httpResponse']:

            for header in csv_http_headers:
                if header in site_data_json['httpResponse']['headers']:
                    result.append(site_data_json['httpResponse']['headers'][header])
                else:
                    result.append('n/a')
        else:
            for c in range(len(csv_http_headers)):
                result.append('')
    else:
        for c in range(len(csv_http_headers)):
            result.append('')

    if 'asnInfo' in site_data_json:
        # sometimes we have local ips in the lookup
        if 'asn' in site_data_json['asnInfo']:
            for data in csv_ip:
                result.append(site_data_json['asnInfo'][data])

        else:
            for c in range(len(csv_ip)):
                result.append('')
    else:
        for c in range(len(csv_ip)):
            result.append('')

    for data in csv_optional:
        if data in site_data_json:
            result.append(site_data_json[data])
        else:
            result.append('')

    port_str = ""
    for data in csv_shodan:
        if 'shodan' in site_data_json:
            if data in site_data_json['shodan']:
                if data == 'ports':
                    for port in site_data_json['shodan']['ports']:
                        port_str = str(port) + "|" + port_str
                    result.append(port_str)
                else:
                    result.append(site_data_json['shodan'][data])
            else:
                result.append('')
        else:
            result.append('')

    if 'httpResponse' in site_data_json:
        if 'htmlSize' in site_data_json['httpResponse']:
            result.append(site_data_json['httpResponse']['htmlSize'])
        else:
            result.append('')
    else:
        result.append('')

    return result
