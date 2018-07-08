'use strict';
exports.handler = (event, context, callback) => {
    
    //Get contents of response
    const response = event.Records[0].cf.response;
    const headers = response.headers;

//Set new headers 
 headers['strict-transport-security'] = [{key: 'Strict-Transport-Security', value: 'max-age=63072000'}]; 
 headers['x-content-type-options'] = [{key: 'X-Content-Type-Options', value: 'nosniff'}]; 
 headers['x-frame-options'] = [{key: 'X-Frame-Options', value: 'DENY'}]; 
 headers['x-xss-protection'] = [{key: 'X-XSS-Protection', value: '1; mode=block'}]; 
 headers['referrer-policy'] = [{key: 'Referrer-Policy', value: 'no-referrer'}]; 

 headers['content-security-policy'] = [{key: 'Content-Security-Policy', value: "default-src 'none'; script-src 'self' https://maxcdn.bootstrapcdn.com https://code.jquery.com; style-src 'self' https://maxcdn.bootstrapcdn.com; upgrade-insecure-requests; form-action 'self'; connect-src 'self' api.govscan.info; img-src 'self'; frame-ancestors 'none'; base-uri 'self'; report-uri https://cspgovscan.report-uri.com/r/d/csp/enforce"}]; 
   
    //Return modified response
    callback(null, response);
};
