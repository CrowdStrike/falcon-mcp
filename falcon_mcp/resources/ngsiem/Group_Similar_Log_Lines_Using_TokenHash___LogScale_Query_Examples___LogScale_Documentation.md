# Group Similar Log Lines Using TokenHash | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-tokenhash-group-similar-logs.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Group Similar Log Lines Using TokenHash

Find patterns in log messages by grouping similar structures using the [`tokenHash()`](https://library.humio.com/data-analysis/functions-tokenhash.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    h := tokenHash(@rawstring)
    groupBy(h, limit=max, function=[ count(), collect(@rawstring, limit=3) ])

### Introduction

The [`tokenHash()`](https://library.humio.com/data-analysis/functions-tokenhash.html) function can be used to identify log messages with similar patterns by creating a hash of the structure of the message while ignoring the specific values. 

In this example, the [`tokenHash()`](https://library.humio.com/data-analysis/functions-tokenhash.html) function is used to group log messages that share the same structure but contain different values. This helps identify common log patterns in your data. 

Note that the purpose of [`tokenHash()`](https://library.humio.com/data-analysis/functions-tokenhash.html) is for grouping related log lines, not for cryptographic use. 

Example incoming data might look like this: 

@timestamp| @rawstring  
---|---  
2023-06-06T10:00:00Z| User john.doe logged in from 192.168.1.100  
2023-06-06T10:01:00Z| User jane.smith logged in from 192.168.1.101  
2023-06-06T10:02:00Z| User admin logged in from 192.168.1.102  
2023-06-06T10:03:00Z| Failed login attempt from 10.0.0.1  
2023-06-06T10:04:00Z| Failed login attempt from 10.0.0.2  
2023-06-06T10:05:00Z| Database connection error: timeout after 30 seconds  
2023-06-06T10:06:00Z| Database connection error: timeout after 45 seconds  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         h := tokenHash(@rawstring)

Creates a hash value based on the structure of the log message in the [@rawstring](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field and returns the token hash in a new field named h. The [`tokenHash()`](https://library.humio.com/data-analysis/functions-tokenhash.html) function identifies words, numbers, and special characters while ignoring their specific values. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(h, limit=max, function=[ count(), collect(@rawstring, limit=3) ])

Groups the events by the token hash in the field h. For each group, it: 

     * Counts the number of events using [`count()`](https://library.humio.com/data-analysis/functions-count.html). 

     * Collects up to three example log messages using [`collect()`](https://library.humio.com/data-analysis/functions-collect.html) on the [@rawstring](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field. 

The [_`limit`_](https://library.humio.com/data-analysis/functions-groupby.html#query-functions-groupby-limit)=max parameter ensures all groups are returned. 

  4. Event Result set.




### Summary and Results

The query is used to identify common log message patterns by grouping similar log lines together, regardless of their specific values. 

This query is useful, for example, to discover the most common types of log messages in your data, identify unusual or rare log patterns that might indicate problems and create log message templates for parsing or monitoring. 

Sample output from the incoming example data: 

h| _count| @rawstring  
---|---|---  
1111b796| 3| User admin logged in from 192.168.1.102 User jane.smith logged in from 192.168.1.101 User john.doe logged in from 192.168.1.100  
356fb767| 2| Failed login attempt from 10.0.0.2 Failed login attempt from 10.0.0.1  
90fadc1e| 2| Database connection error: timeout after 45 seconds Database connection error: timeout after 30 seconds  
  
Note that logs with the same structure but different values are grouped together, making it easy to identify common patterns in your log data.
