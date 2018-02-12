def format_response(result):
    history_elapsed = 0
    response = dict()

    response["statusCode"] = result.status_code

    if result.status_code in [200, 203]:
        response["contentSize"] = len(result.content)

        if result.history:
            response["redirectCount"] = len(result.history)
            response["redirectUrl"] = result.url

            if result.url[4] in ['S', 's']:
                response["redirectHttps"] = True
            else:
                response["redirectHttps"] = False

            for history in result.history:
                history_elapsed = history_elapsed + history.elapsed.microseconds

        else:
            response["redirectHttps"] = False

        response["responseTime"] = result.elapsed.microseconds + history_elapsed

        for header_field in result.headers._store.items():
            response[header_field[1][0]] = header_field[1][1]

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
    cert_data = dict()

    cert_data["tlsServerNameIndication"] = scan_result.server_info.tls_server_name_indication
    cert_data["highestSslVersionSupported"] = str(scan_result.server_info.highest_ssl_version_supported)
    cert_data["sslCipherSupported"] = scan_result.server_info.ssl_cipher_supported
    cert_data["certificateMatchesHostname"] = scan_result.certificate_matches_hostname
    cert_data["serialNumber"] = scan_result.certificate_chain[0].serial_number

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
