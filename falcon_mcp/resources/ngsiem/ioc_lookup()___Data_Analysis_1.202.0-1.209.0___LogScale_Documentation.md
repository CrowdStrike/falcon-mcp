# ioc:lookup() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-ioc-lookup.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)")

Look up IOCs (Indicators of Compromise) of IP addresses, URLs and domains in a local copy of CrowdStrike's curated database of IOCs and annotate the events with the associated security information. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`confidenceThreshold`_](functions-ioc-lookup.html#query-functions-ioc-lookup-confidencethreshold)|  string| optional[a] | [`high`](functions-ioc-lookup.html#query-functions-ioc-lookup-confidencethreshold-option-high)|  The lowest level of confidence of IOCs to consider.   
|  |  | **Values**  
|  |  | [`unverified`](functions-ioc-lookup.html#query-functions-ioc-lookup-confidencethreshold-option-unverified)| IOC for this item has been reported but not yet verified; will return all of the available confidence levels for the item  
|  |  | [`low`](functions-ioc-lookup.html#query-functions-ioc-lookup-confidencethreshold-option-low)| Low level of confidence that the item is an IOC (and higher)  
|  |  | [`medium`](functions-ioc-lookup.html#query-functions-ioc-lookup-confidencethreshold-option-medium)| Medium level of confidence that the item is an IOC (and higher)  
|  |  | [`high`](functions-ioc-lookup.html#query-functions-ioc-lookup-confidencethreshold-option-high)| High level of confidence that the item is an IOC  
[ _`field`_](functions-ioc-lookup.html#query-functions-ioc-lookup-field)[b]| array of strings| required |  |  The field(s) containing either IP addresses, URLs or domains to check for IOCs.   
[_`include`_](functions-ioc-lookup.html#query-functions-ioc-lookup-include)|  array of strings| optional[[a]](functions-ioc-lookup.html#ftn.table-functions-ioc-lookup-optparamfn) | `All columns`|  Specifies the columns from the IOC database to include.   
|  |  | **Values**  
|  |  | [`indicator`](functions-ioc-lookup.html#query-functions-ioc-lookup-include-option-indicator)| The IOC found in the event  
|  |  | [`labels`](functions-ioc-lookup.html#query-functions-ioc-lookup-include-option-labels)| One or more labels indicating the IOC information  
|  |  | [`last_updated`](functions-ioc-lookup.html#query-functions-ioc-lookup-include-option-last_updated)| The date the IOC was last updated  
|  |  | [`malicious_confidence`](functions-ioc-lookup.html#query-functions-ioc-lookup-include-option-malicious_confidence)| The confidence level of the IOC, `high`, `medium`,`low`, or `unverified`  
|  |  | [`published_date`](functions-ioc-lookup.html#query-functions-ioc-lookup-include-option-published_date)| The date the IOC was first published  
|  |  | [`type`](functions-ioc-lookup.html#query-functions-ioc-lookup-include-option-type)| The type of the IOC detected, `ip_address`, `url`, or `domain`  
[ _`prefix`_](functions-ioc-lookup.html#query-functions-ioc-lookup-prefix)|  string| optional[[a]](functions-ioc-lookup.html#ftn.table-functions-ioc-lookup-optparamfn) | `ioc`|  Prefix for the names of all the output fields.   
[_`strict`_](functions-ioc-lookup.html#query-functions-ioc-lookup-strict)|  boolean| optional[[a]](functions-ioc-lookup.html#ftn.table-functions-ioc-lookup-optparamfn) | [`false`](functions-ioc-lookup.html#query-functions-ioc-lookup-strict-option-false)|  If `true`, only output events where at least one of the selected fields matches an IOC; if `false` (the default), let all events through.   
|  |  | **Values**  
|  |  | [`false`](functions-ioc-lookup.html#query-functions-ioc-lookup-strict-option-false)| Pass all events  
|  |  | [`true`](functions-ioc-lookup.html#query-functions-ioc-lookup-strict-option-true)| Only output events where at least one of the selected fields matches an IOC  
[ _`type`_](functions-ioc-lookup.html#query-functions-ioc-lookup-type)|  string| required |  |  Specifies the type of IOCs to search for a match. Specifying the wrong type may lead to inconsistent or inconclusive results.   
|  |  | **Values**  
|  |  | [`domain`](functions-ioc-lookup.html#query-functions-ioc-lookup-type-option-domain)| Source value is a domain or hostname  
|  |  | [`ip_address`](functions-ioc-lookup.html#query-functions-ioc-lookup-type-option-ip_address)| Source value is an IP address  
|  |  | [`url`](functions-ioc-lookup.html#query-functions-ioc-lookup-type-option-url)| Source value is a URL  
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-ioc-lookup.html#query-functions-ioc-lookup-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-ioc-lookup.html#query-functions-ioc-lookup-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     ioc:lookup(["value"],type="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     ioc:lookup(field=["value"],type="value")
> 
> These examples show basic structure only.

Hide negatable operation for this function

Show negatable operation for this function

> Negatable Function Operation
> 
> This function is negatable, implying the inverse of the result. For example:
> 
> logscale Syntax
>     
>     
>     !ioc:lookup()
> 
> Or:
> 
> logscale Syntax
>     
>     
>     not ioc:lookup()
> 
> For more information, see [Negating the Result of Filter Functions](syntax-operators.html#syntax-operators-negate "Negating the Result of Filter Functions").

### [`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)") Function Operation

### Important

The [`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)") function cannot be used to lookup custom indicators when deployed within a multi-tenant environment. 

If any of the selected fields match an IOC, the field ioc (by default, controlled via the [_`prefix`_](functions-ioc-lookup.html#query-functions-ioc-lookup-prefix) parameter) will be added to each event. If an IOC is identified, the returned information will be an array of values prefix.detected will be added to the event with the value `true`, where prefix is the value of the `prefix` argument. 

Detailed information on the IOC will then be added to an array ioc (or [_`prefix`_](functions-ioc-lookup.html#query-functions-ioc-lookup-prefix) parameter). For example: 

ioc.detected| ioc[0].indicator| ioc[0].labels| ioc[0].last_updated| ioc[0].malicious_confidence| ioc[0].published_date| ioc[0].type  
---|---|---|---|---|---|---  
true| 91.92.242.184| KillChain/C2,Malware/AsyncRAT,Malware/Remcos,ThreatType/Commodity,ThreatType/CredentialHarvesting,ThreatType/Criminal,ThreatType/Modular,ThreatType/OpenSource,ThreatType/RAT| 1706062241000| unverified| 1703421875000| ip_address  
  
IP addresses can be either IPv4 or IPv6 addresses. Short-hand notation for IPv6 addresses is supported and can be matched against non-short-hand notation. URLs and domains use case-insensitive string matching. 

The function can be negated, but only with [_`strict=true`_](functions-ioc-lookup.html#query-functions-ioc-lookup-strict). 

For information about how to configure the IOC database, see [IOC Configuration](https://library.humio.com/deployment/configuration-ioc.html). 

#### Returned Fields

The function will set ioc.detected to `true` for any event that has an identified indicator of compromise. Additional fields then contain specific information about the IOC trigger. 

By default, a full set of fields is returned, and because an entry could match one or more IOCs, the information is returned as an array for each of these fields. The returned fields can be limited by using the [_`include`_](functions-ioc-lookup.html#query-functions-ioc-lookup-include) argument. For example: 

logscale
    
    
    ioc:lookup(field=[lookupfield], type="domain",include=["labels", "type"])

Might return: 

@id| ioc.detected| ioc[0].labels| ioc[0].malicious_confidence| lookupfield  
---|---|---|---|---  
9ihO66MGBDUAtd1snMEbrWFR_3_44_1709295971| true| MaliciousConfidence/High,Malware/AsyncRAT,ThreatType/Commodity,ThreatType/Criminal,ThreatType/Modular,ThreatType/OpenSource,ThreatType/RAT| high| doinhulon.ddns.net  
  
The list of fields that can be returned and their contents are described in the table below: 

Column |  Type |  Description   
---|---|---  
indicator |  string |  The IOC that was found in the event field.   
type |  string |  The type of IOC detected. One of `ip_address`, `url`, and domain.   
published_date |  Timestamp in Unix time, UTC |  The date the IOC was first published.   
last_updated |  Timestamp in Unix time, UTC |  The date the IOC was last updated.   
malicious_confidence |  string |  The confidence level by which an IOC is considered to be malicious. Malicious confidence changes over time, since it is determine as a vector combining the level of the malicious activity and how recently that activity has been seen in active use. More recent active malicious activity is given a higher confience level. 

  * `high`: The IOC has been associated with malicious activity within the last 60 days. 
  * `medium`: The IOC has been associated with malicious activity within the last 60-120 days. 
  * `low`: The IOC has been associated with malicious activity exceeding 120 days. 
  * `unverified`: The IOC has not been verified by a CrowdStrike Intelligence analyst or an automated system. 

  
labels |  string |  Detailed information about the IOC using a comma-separated list of labels. See [Labels](functions-ioc-lookup.html#functions-ioc-lookup-labels "Labels").   
  
##### Labels

The column labels contains a comma-separated list of labels that provide additional context around an indicator. The labels have the form `category/value`. The categories are described below. 

###### Actors

Have the form `Actor/...`. 

The named actor that the indicator is associated with (for example, `Panda`, `Bear`, `Spider`, etc). 

###### Malware Families

Have the form `Malware/...`. 

Indicates the malware family an indicator has been associated with (for example, `Malware/PoisonIvy`, `Malware/Zeus`, `Malware/DarkComet`, etc). An indicator may be associated with more than one malware family. 

###### Kill Chains

Have the form `KillChain/...`. 

The point in the kill chain at which an indicator is associated. 

  * `KillChain/Reconnaissance`: This indicator is associated with the research, identification, and selection of targets by a malicious actor. 

  * `KillChain/Weaponization`: This indicator is associated with assisting a malicious actor create malicious content. 

  * `KillChain/Delivery`: This indicator is associated with the delivery of an exploit or malicious payload. 

  * `KillChain/Exploitation`: This indicator is associated with the exploitation of a target system or environment. 

  * `KillChain/Installation`: This indicator is associated with the installation or infection of a target system with a remote access tool or other tool allowing for persistence in the target environment. 

  * `KillChain/C2` (Command and Control): This indicator is associated with malicious actor command and control. 

  * `KillChain/ActionOnObjectives`: This indicator is associated with a malicious actor's desired effects and goals. 




###### Domain Types

Have the form `DomainType/...`. 

  * `DomainType/ActorControlled`: It is believed the malicious actor is still in control of this domain. 

  * `DomainType/DGA`: This domain is the result of malware utilizing a domain generation algorithm. 

  * `DomainType/DynamicDNS`: This domain is owned or used by a dynamic DNS service. 

  * `DomainType/DynamicDNS/Afraid`: This domain is owned or used by the Afraid.org dynamic DNS service. 

  * `DomainType/DynamicDNS/DYN`: This domain is owned or used by the DYN dynamic DNS service. 

  * `DomainType/DynamicDNS/Hostinger`: This domain is owned or used by the Hostinger dynamic DNS service. 

  * `DomainType/DynamicDNS/noIP`: This domain is owned or used by the NoIP dynamic DNS service. 

  * `DynamicDNS/Oray`: This domain is owned or used by the Oray dynamic DNS service. 

  * `DomainType/KnownGood`: The domain itself (or the domain portion of a URL) is known to be legitimate, despite having been associated with malware or malicious activity. 

  * `DomainType/LegitimateCompromised`: This domain does not typically pose a threat but has been compromised by a malicious actor and may be serving malicious content. 

  * `DomainType/PhishingDomain`: This domain has been observed to be part of a phishing campaign. 

  * `DomainType/Sinkholed`: The domain is being sinkholed, likely by a security research team. This indicates that, while traffic to the domain likely has a malicious source, the IP address to which it is resolving is controlled by a legitimate 3rd party. It is no longer believed to be under the control of the actor. 

  * `DomainType/StrategicWebCompromise`: While similar to the `DomainType/LegitimateCompromised` label, this label indicates that the activity is of a more targeted nature. Oftentimes, targeted attackers will compromise a legitimate domain that they know to be a watering hole frequently visited by the users at the organizations they are looking to attack. 

  * `DomainType/Unregistered`: The domain is not currently registered with any registrars. 




###### IP Address Types

Have the form `IPAddressType/...`. 

  * `IPAddressType/HtranDestinationNode`: An IP address with this label is being used as a destination address with the HTran Proxy Tool. 

  * `IPAddressType/HtranProxy`: An IP address with this label is being used as a relay or proxy node with the HTran Proxy Tool. 

  * `IPAddressType/LegitimateCompromised`: It is suspected an IP address with this label is compromised by malicious actors. 

  * `IPAddressType/Parking`: This IP address is likely being used as parking IP address. 

  * `IPAddressType/PopularSite`: This IP address could be utilized for a variety of purposes and may appear more frequently than other IPs. 

  * `IPAddressType/SharedWebHost`: This IP address may be hosting more than one website. 

  * `IPAddressType/Sinkhole`: This IP address is likely a sinkhole being operated by a security researcher or vendor. 

  * `IPAddressType/TorProxy`: This IP address is acting as a TOR (The Onion Router) Proxy. 




###### Status

Have the form `Status/...`. 

  * `Status/ConfirmedActive`: This indicator is likely to be currently supporting malicious activity. 

  * `Status/ConfirmedInactive`: This indicator is no longer used for malicious purposes. 

  * `Status/Historic`: The indicator is no longer used for malicious purposes but could be used again in the future. 




###### Target

Have the form `Target/...`. 

The activity associated with this indicator is known to target the indicated vertical sector, which could be any of the following: 

  * `Target/Aerospace`

  * `Target/Agricultural`

  * `Target/Chemical`

  * `Target/Defense`

  * `Target/Dissident`

  * `Target/Energy`

  * `Target/Extractive`

  * `Target/Financial`

  * `Target/Government`

  * `Target/Healthcare`

  * `Target/Insurance`

  * `Target/InternationalOrganizations`

  * `Target/Legal`

  * `Target/Manufacturing`

  * `Target/Media`

  * `Target/>NGO`

  * `Target/Pharmaceutical`

  * `Target/Research`

  * `Target/Retail`

  * `Target/Shipping`

  * `Target/Technology`

  * `Target/Telecom`

  * `Target/Transportation`

  * `Target/Universities`




###### Threat Type

Have the form `ThreatType/...`. 

  * `ThreatType/ClickFraud`: This indicator is used by actors engaging in click or ad fraud 

  * `ThreatType/Commodity`: This indicator is used with commodity type malware such as Zeus or Pony Downloader. 

  * `ThreatType/PointOfSale`: This indicator is associated with activity known to target point-of-sale machines such as AlinaPoS or BlackPoS. 

  * `ThreatType/Ransomware`: This indicator is associated with ransomware malware such as Crytolocker or Cryptowall. 

  * `ThreatType/Suspicious`: This indicator is not currently associated with a known threat type but should be considered suspicious. 

  * `ThreatType/Targeted`: This indicator is associated with a known actor suspected to associated with a nation-state such as `DEEP PANDA` or `ENERGETIC BEAR`. 

  * `ThreatType/TargetedCrimeware`: This indicator is associated with a known actor suspected to be engaging in criminal activity such as `WICKED SPIDER`. 




###### Vulnerability

Have the form `Vulnerability/...`. 

The CVE-XXXX-XXX vulnerability the indicator is associated with (for example, `Vulnerability/CVE-2012-0158`). 

##### Testing

If you use this function in a query and it does not produce any IOC results, it can be hard to tell whether there were no results or there is an error in the query. To help with that, we provide some sample IOCs that you can test your query with: 

Type |  Sample   
---|---  
IP address |  `45.32.129.185`  
Domain |  `misdepatrment.com`  
URL |  `http://mail.cosmeticsurgerypune.com`  
  
Since the IOC database is updated constantly, we cannot guarantee that these remain in the database. If you believe that one of them is no longer in the database, please contact us. Also, the malicious_confidence of these IOCs will probably be lowered over time. 

For example, to test the IP address you can run the query: 

logscale
    
    
    createEvents("client_ip=38.92.47.91") 
    | kvParse()
    | ioc:lookup(field=[client_ip],type="ip_address",confidenceThreshold=unverified)

Might output: 

ioc.detected| ioc[0].indicator| ioc[0].labels| ioc[0].last_updated| ioc[0].malicious_confidence| ioc[0].published_date| ioc[0].type  
---|---|---|---|---|---|---  
true| 167.235.59.196| IPAddressType/C2,KillChain/C2,MaliciousConfidence/High,Malware/ScreenConnectClickOnce,ThreatType/LegitimateSoftware| 1738574171000| high| 1738572221000| ip_address  
  
##### Parser Behavior with Missing Database

When using [`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)") in parser queries, the function may encounter dependency issues due to missing or temporary unavailable IOC database. In such cases, the parser continues processing data normally but generates a warning message. See [Parser Warning](parsers-create.html#parser-warning) for more information. 

### [`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)") Examples

Click + next to an example below to get the full details.

#### Look Up IP Addresses with Custom Detection Prefix

**Look Up IP Addresses to detect malicious IP addresses using the[`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)") function with [_`prefix`_](functions-ioc-lookup.html#query-functions-ioc-lookup-prefix) parameter to customize output fields **

##### Query

logscale
    
    
    ioc:lookup(src_ip, type="ip_address", prefix="detection", confidenceThreshold=low)

##### Introduction

In this example, the [`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)") function is used to check source IP addresses against IOC lists, with results stored in fields prefixed with `detection`. 

Example incoming data might look like this: 

@timestamp| src_ip| dst_ip| bytes_transferred| connection_status  
---|---|---|---|---  
2025-08-06T10:15:30.000Z| 192.168.1.100| 45.33.32.156| 1544| success  
2025-08-06T10:15:31.000Z| 192.168.1.101| 185.159.83.24| 2048| success  
2025-08-06T10:15:32.000Z| 192.168.1.102| 172.16.0.100| 856| success  
2025-08-06T10:15:33.000Z| 192.168.1.103| 91.245.73.85| 1028| success  
2025-08-06T10:15:34.000Z| 192.168.1.104| 10.0.0.50| 922| success  
2025-08-06T10:15:35.000Z| 45.32.129.185| 10.0.0.50| 922| success  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         ioc:lookup(src_ip, type="ip_address", prefix="detection", confidenceThreshold=low)

Performs an IOC lookup on the src_ip field. 

The [_`type`_](functions-ioc-lookup.html#query-functions-ioc-lookup-type) parameter is set to `ip_address` to specify the type of data being looked up. The [_`prefix`_](functions-ioc-lookup.html#query-functions-ioc-lookup-prefix) parameter is set to `detection` to customize the prefix of added output fields. By default, if no matches are found, no additional fields are added to the event. The function automatically checks both IPv4 and IPv6 addresses. 

The [_`confidenceThreshold`_](functions-ioc-lookup.html#query-functions-ioc-lookup-confidencethreshold) parameter is set to `low` to include matches with low confidence ratings. 

When matches are found, the function adds several fields with the prefix detection containing detailed information about the matched indicator. 

  3. Event Result set.




##### Summary and Results

The query is used to identify potentially malicious source IP addresses by checking them against CrowdStrike's IOC database, including low confidence matches and store the detection information in custom-prefixed fields. 

This query is useful, for example, to detect all potential security threats in network traffic, even those with lower confidence ratings, enabling comprehensive threat analysis, identify potential security threats, and enrich events with CrowdStrike's threat intelligence information. Furthermore, the query is useful to integrate IOC detection results with existing security workflows that expect specific field naming conventions. 

Sample output from the incoming example data: 

@timestamp| @timestamp.nanos| @timezone| bytes_transferred| connection_status| detection.detected| detection[0].indicator| detection[0].labels| detection[0].last_updated| detection[0].malicious_confidence| detection[0].published_date| detection[0].type| dst_ip| src_ip  
---|---|---|---|---|---|---|---|---|---|---|---|---|---  
1754475330000| 0| Z| 1544| success| <no value>| <no value>| <no value>| <no value>| <no value>| <no value>| <no value>| 45.33.32.156| 192.168.1.100  
1754475331000| 0| Z| 2048| success| <no value>| <no value>| <no value>| <no value>| <no value>| <no value>| <no value>| 185.159.83.24| 192.168.1.101  
1754475332000| 0| Z| 856| success| <no value>| <no value>| <no value>| <no value>| <no value>| <no value>| <no value>| 172.16.0.100| 192.168.1.102  
1754475333000| 0| Z| 1028| success| <no value>| <no value>| <no value>| <no value>| <no value>| <no value>| <no value>| 91.245.73.85| 192.168.1.103  
1754475334000| 0| Z| 922| success| <no value>| <no value>| <no value>| <no value>| <no value>| <no value>| <no value>| 10.0.0.50| 192.168.1.104  
1754475335000| 0| Z| 922| success| true| 45.32.129.185| Actor/FANCYBEAR,IPAddressType/AdversaryControlled,KillChain/ActionOnObjectives,KillChain/C2,MaliciousConfidence/Low,Malware/Meterpreter,Malware/Xtunnel,ThreatType/Criminal,ThreatType/Proxy,ThreatType/Targeted| 1752747451000| low| 1463063677000| ip_address| 10.0.0.50| 45.32.129.185  
  
Note that the detection.detected field indicates whether a match was found, and that matched events contain detailed threat intelligence in the detection[0] fields. 

Labels provide context about the threat actor, malware types, and threat categories. For more details, see [`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)"). 

#### Look up IP address IOCs

**Look up IP address Indicators of Compromise (IOCs) in the IP field using the[`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)") function **

##### Query

logscale
    
    
    ioc:lookup(field=ip, type=ip_address)

##### Introduction

In this example, the [`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)") function is used to search for IOCs for IP addresses in the ip field where the IP address is marked with a confidence threshold of high and annotate events with the associated security information. As default, without explicitly setting different arguments, the [_`confidenceThreshold`_](functions-ioc-lookup.html#query-functions-ioc-lookup-confidencethreshold) parameter is set to `high`. 

By default, a full set of fields is returned, and because an entry could match one or more IOCs, the information is returned as an array for each of these fields. The returned fields can be limited by using the [_`include`_](functions-ioc-lookup.html#query-functions-ioc-lookup-include) parameter. The returned results can be limited by using the [_`strict`_](functions-ioc-lookup.html#query-functions-ioc-lookup-strict) parameter. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         ioc:lookup(field=ip, type=ip_address)

Specifies which field to check for IOCs, in this case IP addresses. The [_`type`_](functions-ioc-lookup.html#query-functions-ioc-lookup-type) of the IOC to detect is `ip_address`. 

Note that the` ioc:lookup()` function only returns the IOC, if the IP address is marked with a confidence threshold of high. Therefore, it may not return anything at all. Lowering confidence thresholds increases matches but may include false positives. 

To explicitly lower the threshold for returned queries, use the following:` ioc:lookup(field=ip, type=ip_address, confidenceThreshold="low")`. This searches for thresholds of low or higher (for example: `low`, `medium` and `high`). 

To explicitly specify fields that should be returned to provide more detail, such as, for example, malicious_confidence and label, use the [_`include`_](functions-ioc-lookup.html#query-functions-ioc-lookup-include) parameter: `ioc:lookup(field=ip, type=ip_address, include=["malicious_confidence", "labels"])`. This will limit the returned fields. 

  3. Event Result set.




##### Summary and Results

The query is used to search for IP address Indicators of Compromise (IOCs) in the ip field and annotate the returned events with the associated security information. In this example, all events are passed through. 

If setting the [_`strict`_](functions-ioc-lookup.html#query-functions-ioc-lookup-strict) parameter to true, it only output events where at least one of the selected fields matches an IOC. Then the query should look like this: `ioc:lookup(field=ip, type=ip_address, strict=true)` to limit the output. 

### Note

If you use the [`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)") function in a query and it does not produce any IOC results, it can be hard to tell whether there were no results or if there is an error in the query. The IOC database is updated constantly. 

#### Look up URL IOCs

**Look up URL Indicators of Compromise (IOCs) in the URL field using the[`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)") function **

##### Query

logscale
    
    
    ioc:lookup("url", type="url", confidenceThreshold="low")

##### Introduction

In this example, the [`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)") function is used to search for IOCs for URLs in the url field where the URL is marked with a confidence threshold of low and annotate events with the associated security information. As default, without explicitly setting different arguments, the [_`confidenceThreshold`_](functions-ioc-lookup.html#query-functions-ioc-lookup-confidencethreshold) parameter is set to `high`. 

By default, a full set of fields is returned, and because an entry could match one or more IOCs, the information is returned as an array for each of these fields. The returned fields can be limited by using the [_`include`_](functions-ioc-lookup.html#query-functions-ioc-lookup-include) parameter. The returned results can be limited by using the [_`strict`_](functions-ioc-lookup.html#query-functions-ioc-lookup-strict) parameter. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         ioc:lookup("url", type="url", confidenceThreshold="low")

Specifies which field to check for IOCs, in this case URL, and searches IOCs of all verified confidence levels, for example, `low`, `medium`, and `high`. The [_`type`_](functions-ioc-lookup.html#query-functions-ioc-lookup-type) of the IOC to detect is `url`. 

Note that the` ioc:lookup()` function returns all the IOCs, as the URL is marked with a confidence threshold of low (`[_`confidenceThreshold`_](functions-ioc-lookup.html#query-functions-ioc-lookup-confidencethreshold)=low`). Lowering confidence thresholds increases matches but may include false positives. 

  3. Event Result set.




##### Summary and Results

The query is used to search for URL Indicators of Compromise (IOCs) in the url field and annotate the returned events with the associated security information. In this example, all events are passed through. 

If setting the [_`strict`_](functions-ioc-lookup.html#query-functions-ioc-lookup-strict) parameter to true, it only output events where at least one of the selected fields matches an IOC. Then the query should look like this: `ioc:lookup("url", type="url", confidenceThreshold="low", strict=true)` to limit the output. Looking up URL IOCs for the field url and only keep the events containing an IOC is useful for finding IOCs in queries used for alerts or scheduled searches. 

### Note

If you use the [`ioc:lookup()`](functions-ioc-lookup.html "ioc:lookup\(\)") function in a query and it does not produce any IOC results, it can be hard to tell whether there were no results or if there is an error in the query. The IOC database is updated constantly.
