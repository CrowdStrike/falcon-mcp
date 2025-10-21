# Look Up IP Addresses with Custom Detection Prefix | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-ioc-lookup-ip-detection-prefix.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Look Up IP Addresses with Custom Detection Prefix

Look Up IP Addresses to detect malicious IP addresses using the [`ioc:lookup()`](https://library.humio.com/data-analysis/functions-ioc-lookup.html) function with [_`prefix`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-prefix) parameter to customize output fields 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    ioc:lookup(src_ip, type="ip_address", prefix="detection", confidenceThreshold=low)

### Introduction

The [`ioc:lookup()`](https://library.humio.com/data-analysis/functions-ioc-lookup.html) function can be used to check if IP addresses match entries in Indicators of Compromise (IOC) lists. The function performs lookups against a local copy of CrowdStrike's curated database of IOCs and enriches matching events with detailed threat intelligence using customizable field prefixes. 

In this example, the [`ioc:lookup()`](https://library.humio.com/data-analysis/functions-ioc-lookup.html) function is used to check source IP addresses against IOC lists, with results stored in fields prefixed with `detection`. 

Example incoming data might look like this: 

@timestamp| src_ip| dst_ip| bytes_transferred| connection_status  
---|---|---|---|---  
2025-08-06T10:15:30.000Z| 192.168.1.100| 45.33.32.156| 1544| success  
2025-08-06T10:15:31.000Z| 192.168.1.101| 185.159.83.24| 2048| success  
2025-08-06T10:15:32.000Z| 192.168.1.102| 172.16.0.100| 856| success  
2025-08-06T10:15:33.000Z| 192.168.1.103| 91.245.73.85| 1028| success  
2025-08-06T10:15:34.000Z| 192.168.1.104| 10.0.0.50| 922| success  
2025-08-06T10:15:35.000Z| 45.32.129.185| 10.0.0.50| 922| success  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         ioc:lookup(src_ip, type="ip_address", prefix="detection", confidenceThreshold=low)

Performs an IOC lookup on the src_ip field. 

The [_`type`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-type) parameter is set to `ip_address` to specify the type of data being looked up. The [_`prefix`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-prefix) parameter is set to `detection` to customize the prefix of added output fields. By default, if no matches are found, no additional fields are added to the event. The function automatically checks both IPv4 and IPv6 addresses. 

The [_`confidenceThreshold`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-confidencethreshold) parameter is set to `low` to include matches with low confidence ratings. 

When matches are found, the function adds several fields with the prefix detection containing detailed information about the matched indicator. 

  3. Event Result set.




### Summary and Results

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

Labels provide context about the threat actor, malware types, and threat categories. For more details, see [`ioc:lookup()`](https://library.humio.com/data-analysis/functions-ioc-lookup.html).
