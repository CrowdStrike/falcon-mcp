# Group First Events by Log Level | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-head-groupby-loglevel.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Group First Events by Log Level

Limit and group events using [`head()`](https://library.humio.com/data-analysis/functions-head.html) and [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) functions 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    head(limit=10)
    groupBy(loglevel)

### Introduction

The [`head()`](https://library.humio.com/data-analysis/functions-head.html) function combined with [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) can be used to analyze the distribution of a limited set of events across specific field values. 

In this example, the [`head()`](https://library.humio.com/data-analysis/functions-head.html) function is used to limit the result set to 100 events, which are then grouped by their log level using the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function. 

Example incoming data might look like this: 

@timestamp| loglevel| service| message| status_code  
---|---|---|---|---  
2025-09-01T10:00:00Z| ERROR| authentication| Failed login attempt| 401  
2025-09-01T10:00:05Z| INFO| authentication| Successful login| 200  
2025-09-01T10:00:10Z| ERROR| database| Connection timeout| 503  
2025-09-01T10:00:15Z| WARN| api| Rate limit approaching| 429  
2025-09-01T10:00:20Z| ERROR| authentication| Invalid token| 401  
2025-09-01T10:00:25Z| INFO| api| Request processed| 200  
2025-09-01T10:00:30Z| DEBUG| database| Query executed| 200  
2025-09-01T10:00:35Z| ERROR| api| Internal error| 500  
2025-09-01T10:00:40Z| INFO| authentication| User logout| 200  
2025-09-01T10:00:45Z| WARN| database| High CPU usage| 200  
2025-09-01T10:00:50Z| DEBUG| api| Cache hit| 200  
2025-09-01T10:00:55Z| ERROR| authentication| Session expired| 401  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head(limit=10)

Returns the first 10 events from the dataset. The [_`limit`_](https://library.humio.com/data-analysis/functions-head.html#query-functions-head-limit) parameter explicitly specifies the number of events to return. The events are returned in the order they were received, starting from the oldest event in the time range. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(loglevel)

Groups the events by the values in the loglevel field. The [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function creates buckets for each unique value and counts the number of events in each bucket. By default, it creates a field named _count containing the number of events in each group. 

  4. Event Result set.




### Summary and Results

The query is used to analyze the distribution of log levels across the first 10 events in the dataset. If `head(limit=100)` it would have returned 100 events. 

This query is useful, for example, to quickly assess the proportion of different log levels in a sample of events or to identify if there is an unusual distribution of log severities. 

Sample output from the incoming example data: 

loglevel| _count  
---|---  
ERROR| 5  
INFO| 3  
WARN| 2  
DEBUG| 2  
  
Note that the output shows the count of events for each log level found within the first 10 events, providing a quick overview of the log level distribution in the sample.
