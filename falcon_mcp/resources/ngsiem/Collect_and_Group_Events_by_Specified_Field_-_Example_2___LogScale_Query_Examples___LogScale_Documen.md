# Collect and Group Events by Specified Field - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-collect-ip-address.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Collect and Group Events by Specified Field - Example 2

Collect and group events by specified field using [`collect()`](https://library.humio.com/data-analysis/functions-collect.html) as part of a [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) operation 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    LocalAddressIP4 = * RemoteAddressIP4 = * aip = *
    | groupBy([LocalAddressIP4, RemoteAddressIP4], function=([count(aip, as=aipCount, distinct=true), collect([aip])]))

### Introduction

The [`collect()`](https://library.humio.com/data-analysis/functions-collect.html) function can be used to collect fields from multiple events into one event as part of a [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) operation. The [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function is used to group together events by one or more specified fields. It is used to extract additional aggregations from the data and then add calculation to it using the [`count()`](https://library.humio.com/data-analysis/functions-count.html)function. 

In this example, the [`collect()`](https://library.humio.com/data-analysis/functions-collect.html) function is used to collect fields from multiple events. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         LocalAddressIP4 = * RemoteAddressIP4 = * aip = *

Filters for all events where the fields LocalAddressIP4, RemoteAddressIP4 and aip are all present. The actual values in these fields do not matter; the query just checks for their existence. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy([LocalAddressIP4, RemoteAddressIP4], function=([count(aip, as=aipCount, distinct=true), collect([aip])]))

Groups the returned results in arrays named LocalAddressIP4 and RemoteAddressIP4, collects all the AIPs (Adaptive Internet Protocol) into an array and performs a count on the field aip. The count of the AIP values is returned in a new field named aipCount. 

  4. Event Result set.




### Summary and Results

The query is used to collect fields from multiple events into one event. Collecting should be used on smaller data sets to create a list (or set, or map, or whatever) when you actually need a list object explicitly (for example, in order to pass it on to some other API). Using [`collect()`](https://library.humio.com/data-analysis/functions-collect.html) on larger data set may cause out of memory as it returns the entire data set. The query is useful for network connection analysis and for identifying potential threats. 

Sample output might look like this: 

LocalAddressIP4| RemoteAddressIP4| aipCount| aip  
---|---|---|---  
192.168.1.100| 203.0.113.50| 3| [10.0.0.1, 10.0.0.2, 10.0.0.3]  
10.0.0.5| 198.51.100.75| 1| [172.16.0.1]  
172.16.0.10| 8.8.8.8| 5| [192.0.2.1, 192.0.2.2, 192.0.2.3, 192.0.2.4, 192.0.2.5]
