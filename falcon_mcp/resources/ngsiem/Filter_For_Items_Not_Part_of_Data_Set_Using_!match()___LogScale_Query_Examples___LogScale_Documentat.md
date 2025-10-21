# Filter For Items Not Part of Data Set Using !match()

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-match-negated-set-difference.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Filter For Items Not Part of Data Set Using `!match()`

Find the set difference using the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function with negation 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    src_ip=*
    | !match("known_ips.csv", field=src_ip)

### Introduction

The [`match()`](https://library.humio.com/data-analysis/functions-match.html) function can be used with a negation to filter for items that are not part of a data set. 

In this example, the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function is used with a negation to search and find IP addresses, that are not part of a known list `known_ips.csv`. 

![](images/venn-seta-not-setb.png)  
---  
  
Example incoming data might look like this: 

timestamp| src_ip| dst_ip| src_port| dst_port| protocol| bytes_sent| bytes_received  
---|---|---|---|---|---|---|---  
2025-04-01T07:00:00Z| 192.168.1.101| 10.0.0.50| 52431| 443| TCP| 1024| 2048  
2025-04-01T07:00:01Z| 172.16.0.24| 8.8.8.8| 33221| 53| UDP| 64| 512  
2025-04-01T07:00:02Z| 192.168.1.150| 172.16.0.100| 49223| 80| TCP| 2048| 4096  
2025-04-01T07:00:03Z| 10.0.0.75| 192.168.1.1| 55678| 22| TCP| 512| 1024  
2025-04-01T07:00:04Z| 192.168.1.200| 1.1.1.1| 44556| 53| UDP| 64| 512  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         src_ip=*

Filters for all events that have a src_ip field. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | !match("known_ips.csv", field=src_ip)

Excludes (filters out) any events where the src_ip field matches entries in the file `known_ips.csv`, and returns a list of IP addresses that are not found in the specified file. The negation operator is used to return non-matching results. 

  4. Event Result set.




### Summary and Results

The query is used to search for unknown or unexpected source IP addresses matched up againt a known list. This is useful for detecting potential security theats and monitoring for unauthorized network access. 

Sample output from the incoming example data: 

timestamp| src_ip| dst_ip| src_port| dst_port| protocol| bytes_sent| bytes_received  
---|---|---|---|---|---|---|---  
2025-04-01T07:00:00Z| 192.168.1.101| 10.0.0.50| 52431| 443| TCP| 1024| 2048  
2025-04-01T07:00:01Z| 172.16.0.24| 8.8.8.8| 33221| 53| UDP| 64| 512
