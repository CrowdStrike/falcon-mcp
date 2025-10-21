# Correlate Inbound Email URLs with Subsequent Access Attempts | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-correlate-email-url-access.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Correlate Inbound Email URLs with Subsequent Access Attempts

Correlate Inbound Email URLs with Subsequent Access Attempts to detect when a malicious URL in an email is subsequently accessed using the [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{Conditional} 3["emailInbound: Table"] 4["emailAccess: Table"] 5[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 2 --> 4 3 --> 5 4 --> 5 5 --> result

logscale
    
    
    ((#repo="abnormal_security" AND #event.module="email-security") OR (#repo="corelight" AND #event.module="ids"))
    | case{
        #Vendor="corelight" 
        | url.prefix := "http://" 
        | url.original := concat([url.prefix,"/",client.address,"/",url.path]); *
    }
    | correlate(
        emailInbound:{#event.module="email-security"},
        emailAccess:{#event.module="ids" 
        | url.original <=> emailInbound.url.original},
        sequence=true,within=1h)

### Introduction

The [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function can be used to match and combine events from multiple queries based on specified field values within a defined time window. The set of returned events will consist of a list of events, identified by their correlation query name, and containing the matching connection fields from each event. 

In this example, the [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) is used to match URLs from inbound emails with subsequent HTTP requests to those URLs within a one-hour window, indicating when recipients click on email link. 

The [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) matches URLs received in emails with subsequent access attempts detected in network traffic, helping identify potential phishing or malicious link interactions. 

Example incoming data might look like this: 

@timestamp| #repo| #event.module| #Vendor| client.address| url.path| url.original| email.from.address| email.to.address  
---|---|---|---|---|---|---|---|---  
2023-06-15T10:00:00Z| abnormal_security| email-security| abnormal| <no value>| <no value>| http://malicious.com/path1| sender@external.com| user1@company.com  
2023-06-15T10:15:30Z| corelight| ids| corelight| 10.0.1.100| path1| <no value>| <no value>| <no value>  
2023-06-15T11:00:00Z| abnormal_security| email-security| abnormal| <no value>| <no value>| http://suspicious.net/offer| phish@bad.com| user2@company.com  
2023-06-15T11:05:45Z| corelight| ids| corelight| 10.0.2.200| offer| <no value>| <no value>| <no value>  
2023-06-15T12:30:00Z| abnormal_security| email-security| abnormal| <no value>| <no value>| http://legitimate.org/docs| partner@vendor.com| user3@company.com  
2023-06-15T12:45:15Z| corelight| ids| corelight| 10.0.3.150| docs| <no value>| <no value>| <no value>  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{Conditional} 3["emailInbound: Table"] 4["emailAccess: Table"] 5[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 2 --> 4 3 --> 5 4 --> 5 5 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         ((#repo="abnormal_security" AND #event.module="email-security") OR (#repo="corelight" AND #event.module="ids"))

Filters for events that are either `email-security` events from the abnormal_security repository OR `ids` (Intrusion Detection System) events from the corelight repository. 

This filter ensures that only relevant events from these two specific security tools are processed for the subsequent correlation analysis. 
  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{Conditional} 3["emailInbound: Table"] 4["emailAccess: Table"] 5[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 2 --> 4 3 --> 5 4 --> 5 5 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | case{
             #Vendor="corelight" 
             | url.prefix := "http://" 
             | url.original := concat([url.prefix,"/",client.address,"/",url.path]); *
         }

The case statement processes events from the `corelight` vendor (`#Vendor="corelight"`) only to standardize their URL format. 

For these events, it first creates a new field named url.prefix containing the value `http://`. Then, using the [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) function, it constructs a complete URL string in a new field named url.original. 

This URL is built by combining the HTTP prefix, followed by a forward slash, then the client's IP address from the client.address field, another forward slash, and finally the URL path from the url.path field. 

The wildcard (*) at the end ensures all other original fields in the events are preserved. 

For example, if an event has client.address=`10.0.1.100` and url.path=`download/file.exe`, the resulting url.original field would contain `http://10.0.1.100/download/file.exe`. This standardization allows for proper correlation with URLs found in email security events. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{Conditional} 3["emailInbound: Table"] 4["emailAccess: Table"] 5[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 2 --> 4 3 --> 5 4 --> 5 5 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | correlate(
             emailInbound:{#event.module="email-security"},

Defines the first query named emailInbound to match email security events. Filters for events with #event.module=`email-security` which captures all inbound emails containing URLs. All fields from matching events are preserved since no field restrictions are specified. 

This query forms the base pattern for correlation, and its fields (particularly url.original) will be referenced by the second query using the prefix notation (emailInbound.url.original). 

These events represent the initial detection of URLs in incoming emails, which is crucial for tracking potential phishing attempts or malicious links. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{Conditional} 3["emailInbound: Table"] 4["emailAccess: Table"] 5[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 2 --> 4 3 --> 5 4 --> 5 5 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         emailAccess:{#event.module="ids" 
             | url.original <=> emailInbound.url.original},

Defines the second query named emailAccess to match URL access attempts. Filters for events with #event.module=`ids` which captures network traffic events. 

The correlation relationship (condition) is specified using the ``<=>`` operator which requires exact matches between fields (field correlation matches). 

The url.original field from this emailAccess event must match the url.original field from the emailInbound event. This ensures that events will only be correlated when they show access to exactly the same URL that was received in an email, helping identify when recipients click on email links. 

  6. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{Conditional} 3["emailInbound: Table"] 4["emailAccess: Table"] 5[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 2 --> 4 3 --> 5 4 --> 5 5 --> result style 5 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         sequence=true,within=1h)

Sets the correlation parameters: 

     * [_`sequence`_](https://library.humio.com/data-analysis/functions-correlate.html#query-functions-correlate-sequence)=`true` ensures that emailInbound events must occur before emailAccess events, preventing matching of access events that occurred before the email was received.Email receipt must occur before URL access 

     * [_`within`_](https://library.humio.com/data-analysis/functions-correlate.html#query-functions-correlate-within)=`1h` specifies a one-hour maximum time window between email receipt and URL access, focusing on immediate user interactions with email links. Access attempts more than an hour after email receipt are excluded. 

  7. Event Result set.




### Summary and Results

The query is used to identify when users click on URLs received in emails by correlating email security events with network traffic events. The [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) matches URLs received in emails with subsequent access attempts detected in network traffic, helping identify potential phishing or malicious link interactions. 

This query is useful, for example, to detect potential security incidents where users interact with phishing emails, track the effectiveness of security awareness training, or monitor for suspicious URL access patterns. 

Sample output from the incoming example data: 

@timestamp| emailInbound.email.from.address| emailInbound.email.to.address| emailInbound.url.original| emailAccess.@timestamp| emailAccess.client.address| TimeBetweenEvents  
---|---|---|---|---|---|---  
2023-06-15T10:00:00Z| sender@external.com| user1@company.com| http://malicious.com/path1| 2023-06-15T10:15:30Z| 10.0.1.100| 930  
2023-06-15T11:00:00Z| phish@bad.com| user2@company.com| http://suspicious.net/offer| 2023-06-15T11:05:45Z| 10.0.2.200| 345  
2023-06-15T12:30:00Z| partner@vendor.com| user3@company.com| http://legitimate.org/docs| 2023-06-15T12:45:15Z| 10.0.3.150| 915
