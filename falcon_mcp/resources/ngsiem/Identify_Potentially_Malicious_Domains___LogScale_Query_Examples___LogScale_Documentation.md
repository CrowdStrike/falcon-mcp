# Identify Potentially Malicious Domains | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-groupby-ioc-lookup-domain-malicious.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Identify Potentially Malicious Domains

Group Domain Names and look up IOC Information using the [`ioc:lookup()`](https://library.humio.com/data-analysis/functions-ioc-lookup.html) function for domain analysis 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    groupBy([DomainName])
    ioc:lookup(field=[DomainName], type="domain", confidenceThreshold=unverified, strict=true)
    table([DomainName, "ioc[0].labels"])

### Introduction

The [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function can be used to group events by specified fields before performing additional operations on the grouped data such as, for example, an IOC Lookup. 

The [`ioc:lookup()`](https://library.humio.com/data-analysis/functions-ioc-lookup.html) function searches for IOCs (Indicators of Compromise) of IP addresses, URLs and domains in a local copy of CrowdStrike's curated database of IOCs and adds security information to the events. If any of the selected fields match an IOC, the field ioc (by default, controlled via the _`ioc:lookup()`_ parameter) will be added to each event. 

In this example, the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function is used to group domain names before performing an IOC lookup to identify potentially malicious domains. 

Example incoming data might look like this: 

@timestamp| DomainName| AccessCount| UserID  
---|---|---|---  
2025-10-06T10:00:00Z| wizard-domain.com| 5| user123  
2025-10-06T10:01:00Z| malicious-wizard.net| 3| user456  
2025-10-065T10:02:00Z| legitimate-site.com| 8| user789  
2025-10-065T10:03:00Z| evil-wizard.org| 2| user123  
2025-10-06T10:04:00Z| wizard-hack.com| 4| user456  
2025-10-06T10:05:00Z| normal-domain.net| 6| user789  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy([DomainName])

Groups the events by the DomainName field, creating a unique list of domain names. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         ioc:lookup(field=[DomainName], type="domain", confidenceThreshold=unverified, strict=true)

Performs an IOC lookup on each domain name in the DomainName field, and returns the results in a field prefixed with ioc. 

The lookup is configured to search for domain-type indicators, include unverified confidence levels, and use strict matching (`true`). 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         table([DomainName, "ioc[0].labels"])

Creates a table displaying the DomainName field and the labels from the first IOC match (ioc[0].labels). 

  5. Event Result set.




### Summary and Results

The query is used to identify domain names that match known indicators of compromise (IOCs) and extract their associated labels. 

This query is useful, for example, to identify potentially malicious domains in your network traffic that contain specific patterns in their IOC labels, such as those related to `wizard` threats. 

Sample output from the incoming example data: 

DomainName| ioc[0].labels  
---|---  
malicious-wizard.net,["wizard-malware","suspicious"]|   
evil-wizard.org,["wizard-campaign","malicious"]|   
wizard-hack.com,["wizard-botnet","dangerous"]|   
  
The labels field contains an array of categorizations for each identified malicious domain.
