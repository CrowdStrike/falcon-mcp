# Get First Events From Result Set | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-head-top-events-results.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Get First Events From Result Set

Limit the number of events returned using the [`head()`](https://library.humio.com/data-analysis/functions-head.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    loglevel=ERROR
    head(10)

### Introduction

The [`head()`](https://library.humio.com/data-analysis/functions-head.html) function can be used to return the first N events from a result set. This is useful for limiting output size and getting a quick preview of data. 

In this example, the [`head()`](https://library.humio.com/data-analysis/functions-head.html) function is used to return the first 10 error events from the event set. 

Example incoming data might look like this: 

@timestamp| loglevel| service| message  
---|---|---|---  
2025-08-06T10:00:00Z| ERROR| authentication| Failed login attempt for user 'admin'  
2025-08-06T10:00:05Z| INFO| authentication| Successful login for user 'john'  
2025-08-06T10:00:10Z| ERROR| database| Connection timeout to primary database  
2025-08-06T10:00:15Z| WARN| api| Rate limit threshold reached  
2025-08-06T10:00:20Z| ERROR| authentication| Invalid credentials provided  
2025-08-06T10:00:25Z| INFO| api| Request processed successfully  
2025-08-06T10:00:30Z| ERROR| database| Query execution failed  
2025-08-06T10:00:35Z| ERROR| api| Internal server error  
2025-08-06T10:00:40Z| INFO| authentication| User logout  
2025-08-06T10:00:45Z| ERROR| database| Index corruption detected  
2025-08-06T10:00:50Z| ERROR| api| Service unavailable  
2025-08-06T10:00:55Z| ERROR| authentication| Account locked due to multiple failures  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         loglevel=ERROR

Filters events where the loglevel field equals `ERROR`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head(10)

Returns the first 10 events from the filtered result set. If no [_`limit`_](https://library.humio.com/data-analysis/functions-head.html#query-functions-head-limit) parameter is specified, the [`head()`](https://library.humio.com/data-analysis/functions-head.html) function defaults to returning 200 events. The events are returned in the order they were received, starting from the oldest event in the time range. 

`head(10)` is equal to `head(limit=10)`. 

  4. Event Result set.




### Summary and Results

The query is used to find the first 10 error events in the event set, helping to identify the earliest error occurrences within the specified time range. 

This query is useful, for example, to quickly investigate the beginning of an incident or to get a sample of error events for troubleshooting. 

Sample output from the incoming example data: 

@timestamp| loglevel| service| message  
---|---|---|---  
2025-08-06T10:00:00Z| ERROR| authentication| Failed login attempt for user 'admin'  
2025-08-06T10:00:10Z| ERROR| database| Connection timeout to primary database  
2025-08-06T10:00:20Z| ERROR| authentication| Invalid credentials provided  
2025-08-06T10:00:30Z| ERROR| database| Query execution failed  
2025-08-06T10:00:35Z| ERROR| api| Internal server error  
2025-08-06T10:00:45Z| ERROR| database| Index corruption detected  
2025-08-06T10:00:50Z| ERROR| api| Service unavailable  
2025-08-06T10:00:55Z| ERROR| authentication| Account locked due to multiple failures  
  
Note that only events with loglevel=`ERROR` are included in the output, and the results are ordered chronologically.
