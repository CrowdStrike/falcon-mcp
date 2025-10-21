# Create Sample Groups Using Hash | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-hash-groupby-sampling.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Sample Groups Using Hash

Create consistent sample groups of events using the [`hash()`](https://library.humio.com/data-analysis/functions-hash.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Function)] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    hash(ip_address, limit=10)
    groupBy(_hash, function=count())

### Introduction

The [`hash()`](https://library.humio.com/data-analysis/functions-hash.html) function can be used to create consistent hash values from field contents, enabling deterministic sampling and grouping of events. 

In this example, the [`hash()`](https://library.humio.com/data-analysis/functions-hash.html) function is used to create sample groups from web server access logs based on IP addresses. This allows for consistent grouping of events from the same IP address while limiting the total number of groups. 

Example incoming data might look like this: 

bytes_sent| ip_address| request_path| status_code| @timestamp  
---|---|---|---|---  
1532| 192.168.1.100| /home| 200| 2023-06-15T10:00:00Z  
892| 192.168.1.201| /notfound| 404| 2023-06-15T10:00:01Z  
2341| 192.168.10.100| /about| 200| 2023-06-15T10:00:02Z  
721| 192.168.15.102| /error| 500| 2023-06-15T10:00:03Z  
1267| 192.168.1.101| /contact| 200| 2023-06-15T10:00:04Z  
1843| 192.168.1.103| /products| 200| 2023-06-15T10:00:05Z  
1654| 192.168.15.100| /cart| 200| 2023-06-15T10:00:06Z  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Function)] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         hash(ip_address, limit=10)

Creates a hash value from the ip_address field and returns the result in a new field named _hash (default). This creates a consistent mapping where the same IP address will always generate the same hash value. 

. 

The [_`limit`_](https://library.humio.com/data-analysis/functions-hash.html#query-functions-hash-limit) parameter is set to `10`, which ensures the hash values are distributed across 10 buckets (0-9). All events with the same value of ip-address ends in the same bucket. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Function)] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(_hash, function=count())

Groups the events by the _hash field. For each group, it counts the number of events and returns the result in a new field named _count. This aggregation reduces the data to show how many events fall into each hash bucket. 

  4. Event Result set.




### Summary and Results

The query is used to create consistent sample groups from large datasets by hashing a field value into a limited number of buckets. 

This query is useful, for example, to analyze patterns in web traffic by sampling IP addresses into manageable groups while maintaining consistency - the same IP address will always hash to the same group. This can help identify behavioral patterns or anomalies in subsets of your traffic. 

Sample output from the incoming example data: 

_hash| _count  
---|---  
2| 1  
3| 1  
6| 1  
8| 3  
9| 1  
  
Note that the hash values remain consistent for the same input, enabling reliable sampling across time periods.
