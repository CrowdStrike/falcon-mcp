# Network and Location Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-network-location.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Network and Location Query Functions

LogScale's network functions can be used to identify or filter networks, IP and network addresses. 

**Table: Network Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`asn([as], [field])`](functions-asn.html "asn\(\)")| [_`field`_](functions-asn.html#query-functions-asn-field)|  |  Determines autonomous system number and organization associated.   
[`cidr([column], field, [file], [negate], [subnet])`](functions-cidr.html "cidr\(\)")| [_`field`_](functions-cidr.html#query-functions-cidr-field)|  |  Filters events using CIDR subnets.   
[`communityId([as], destinationip, [destinationport], [icmpcode], [icmptype], proto, [seed], sourceip, [sourceport])`](functions-communityid.html "communityId\(\)")|  |  |  Computes the Community ID, a standard for hashing network flows.   
[`ipLocation([as], [field])`](functions-iplocation.html "ipLocation\(\)")| [_`field`_](functions-iplocation.html#query-functions-iplocation-field)|  |  Determines country, city, longitude, and latitude for given IP address.   
[`rdns([as], field, [limit], [server])`](functions-rdns.html "rdns\(\)")| [_`field`_](functions-rdns.html#query-functions-rdns-field)|  |  Events using RDNS lookup.   
[`shannonEntropy([as], field)`](functions-shannonentropy.html "shannonEntropy\(\)")| [_`field`_](functions-shannonentropy.html#query-functions-shannonentropy-field)|  |  Calculates a entropy measure from a string of characters.   
[`subnet([as], bits, field)`](functions-subnet.html "subnet\(\)")| [_`field`_](functions-subnet.html#query-functions-subnet-field)|  |  Computes a subnet from a IPV4 field.   
[`urlDecode([as], field)`](functions-urldecode.html "urlDecode\(\)")| [_`field`_](functions-urldecode.html#query-functions-urldecode-field)|  |  URL-decodes the contents of a string field.   
[`urlEncode([as], field, [type])`](functions-urlencode.html "urlEncode\(\)")| [_`field`_](functions-urlencode.html#query-functions-urlencode-field)|  |  URL encodes the contents of a string field.
