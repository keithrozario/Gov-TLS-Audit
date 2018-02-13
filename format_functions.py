
def copy_over(source_dict, destination_dict, source_field, destination_field, field_type='keyValue'):

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


def format_site_data(site_data):
    result = dict()

    result = copy_over(site_data, result, 'hostname', 'hostname', 'keyValue')
    result = copy_over(site_data, result, 'ip', 'ip', 'keyValue')
    result = copy_over(site_data, result, 'url', 'url', 'keyValue')

    request_dicts = ['httpRequest', 'httpsRequest']
    response_dicts = ['httpResponse', 'httpsResponse']
    certData_dict = 'certData'

    for request_dict in request_dicts:
        if request_dict in site_data:
            result[request_dict] = dict()
            result[request_dict] = copy_over(site_data[request_dict], result[request_dict],
                                             'headers', 'headers', 'keyValue')
            result[request_dict] = copy_over(site_data[request_dict], result[request_dict],
                                             'requestTime', 'requestTime', 'keyValue')
            result[request_dict] = copy_over(site_data[request_dict], result[request_dict],
                                             'requestUrl', 'requestUrl', 'keyValue')

    for response_dict in response_dicts:
        if response_dict in site_data:
            result[response_dict] = dict()
            result[response_dict] = copy_over(site_data[response_dict], result[response_dict],
                                              'status_code', 'statusCode', 'attribute')
            result[response_dict] = copy_over(site_data[response_dict], result[response_dict],
                                              'url', 'url', 'attribute')
            result[response_dict] = copy_over(site_data[response_dict], result[response_dict],
                                              'history', 'history', 'attribute')
            result[response_dict] = copy_over(site_data[response_dict], result[response_dict],
                                              'content', 'content', 'attribute')

            if hasattr(site_data[response_dict], 'headers'):
                if hasattr(site_data[response_dict].headers, '_store'):
                    result[response_dict]['headers'] = {}
                    for header_field in site_data['httpResponse'].headers._store.items():
                        result[response_dict]['headers'][header_field[1][0]] = header_field[1][1]

    if 'certData' in site_data:
        result[certData_dict] = dict()
        result[certData_dict] = copy_over(site_data[certData_dict], result[certData_dict],
                                          'certificate_matches_hostname', 'certMatchesHostname', 'attribute')
    return result


def format_response(result):
    history_elapsed = 0
    response = dict()

    response["statusCode"] = result.status_code

    if result.status_code in [200, 203]:
        response["contentSize"] = len(result.content)

        if result.history:
            for history in result.history:
                history_elapsed = history_elapsed + history.elapsed.microseconds
        else:
            response["responseTime"] = result.elapsed.microseconds + history_elapsed

    return response


def get_substring(full_string, begin, end):

    substring_start = full_string.find(begin) + len(begin)
    substring_end = full_string[substring_start:].find(end)
    substring = full_string[substring_start:substring_start+substring_end]

    return substring


def parse_attribute(attribute):

    result = []
    name_begin = "name="
    name_end = ")"
    value_begin = "value='"
    value_end = "'"

    result.append(get_substring(attribute, name_begin, name_end))
    result.append(get_substring(attribute, value_begin, value_end))

    return result


def format_cert(scan_result):


    if not cert_data["certificateMatchesHostname"]:
        logger.info("Invalid Cert")

    if scan_result.successful_trust_store:
        cert_data["successfulValidation"] = True
        cert_data["trustStoreName"] = scan_result.successful_trust_store.name
    else:
        cert_data["successfulValidation"] = False

    cert_data["notValidAfter"] = scan_result.certificate_chain[0].not_valid_after
    cert_data["notValidBefore"] = scan_result.certificate_chain[0].not_valid_before
    if scan_result.certificate_chain[0].not_valid_after < datetime.now():
        cert_data["certExpired"] = True
    else:
        cert_data["certExpired"] = False

    cert_data["chainLength"] = len(scan_result.certificate_chain)

    cert_data["issuer"] = dict()
    for attribute in scan_result.certificate_chain[0].issuer._attributes:
        key_value = parse_attribute(str(attribute))
        cert_data["issuer"][key_value[0]] = key_value[1]

    # for extension in scan_result.certificate_chain[0].extensions._extensions:
    #    print(parse_attribute(str(extension)))

    return cert_data
