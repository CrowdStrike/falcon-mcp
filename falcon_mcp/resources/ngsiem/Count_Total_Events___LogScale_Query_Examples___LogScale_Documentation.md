# Count Total Events | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-stats-function-count.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Count Total Events

Count total events using the [`stats()`](https://library.humio.com/data-analysis/functions-stats.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    stats(function=count())

### Introduction

The [`stats()`](https://library.humio.com/data-analysis/functions-stats.html) function can be used to perform aggregate calculations across all events, with [`count()`](https://library.humio.com/data-analysis/functions-count.html) being commonly used to count the total number of events. 

In this example, the [`stats()`](https://library.humio.com/data-analysis/functions-stats.html) is used with [`count()`](https://library.humio.com/data-analysis/functions-count.html) to calculate the total number of events in the result set. 

Example incoming data might look like this: 

@timestamp| status_code| endpoint| response_time  
---|---|---|---  
1686837825000| 200| /api/users| 145  
1686837826000| 404| /api/products| 89  
1686837827000| 200| /api/orders| 167  
1686837828000| 500| /api/payment| 890  
1686837829000| 200| /api/users| 156  
1686837830000| 404| /api/items| 78  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         stats(function=count())

Counts the total number of events in the result set. The [`count()`](https://library.humio.com/data-analysis/functions-count.html) function is passed as an argument to [`stats()`](https://library.humio.com/data-analysis/functions-stats.html) and returns the count in a field named _count. 

The query is actually equivalent to just [`count()`](https://library.humio.com/data-analysis/functions-count.html). 

  3. Event Result set.




### Summary and Results

The query is used to get a simple count of the total number of events matching the query. 

This query is useful, for example, to monitor event volumes, verify data ingestion, or get quick counts of specific event types when combined with filters. 

Sample output from the incoming example data: 

_count  
---  
6  
  
Note that only one row is returned containing the total count
