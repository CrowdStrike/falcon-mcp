# Detect Event A Happening X Times Before Event B Within a Specific Timespan | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-slidingtimewindow-groupby-detect-event-a.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Detect Event A Happening X Times Before Event B Within a Specific Timespan

Detect event A happening X times before event B within a specific timespan using the [`slidingTimeWindow()`](https://library.humio.com/data-analysis/functions-slidingtimewindow.html) function combined with [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result

logscale
    
    
    head()
    | groupBy(
        key,
        function=slidingTimeWindow(
            [{status="failure" | count(as=failures)}, selectLast(status)],
            span=3s
        )
      )
    | failures >= 3
    | status = "success"

### Introduction

In this example, the [`slidingTimeWindow()`](https://library.humio.com/data-analysis/functions-slidingtimewindow.html) function is used with the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function to detect event A happening X times before event B within a specific timespan. 

The query will detect instances where there are 3 or more failed attempts followed by a successful attempt, all occurring within a 3-second window. 

Note that the [`slidingTimeWindow()`](https://library.humio.com/data-analysis/functions-slidingtimewindow.html) function must be used after an aggregator function to ensure event ordering. Also note that the events must be sorted in order by timestamp to prevent errors when running the query. It is possible to select any field to use as a timestamp. 

Example incoming data might look like this: 

@timestamp| key| status  
---|---|---  
1451606300200| c| failure  
1451606300400| c| failure  
1451606300600| c| failure  
1451606301000| a| failure  
1451606302000| a| failure  
1451606302200| a| failure  
1451606302300| a| failure  
1451606302400| b| failure  
1451606302500| a| failure  
1451606302600| a| success  
1451606303200| b| failure  
1451606303300| c| success  
1451606303400| b| failure  
1451606304500| a| failure  
1451606304600| a| failure  
1451606304700| a| failure  
1451606304800| a| success  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head()

Selects the oldest events ordered by time. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy(
             key,
             function=slidingTimeWindow(
                 [{status="failure" | count(as=failures)}, selectLast(status)],
                 span=3s
             )
           )

Groups the events by a specified key (for example, a user ID or IP address), then creates a sliding time window of 3 seconds (with a span of 3 seconds). 

Furthermore, it filters all the failed attempts where the field status contains the value `failure`, makes a count of all the failed attempts, and returns the results in a field named failures, calculates the timespan of the failures, retrieves the timestamp of the last failure, and selects the status of the last event. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | failures >= 3

Filters for windows with 3 or more failures. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | status = "success"

Filters for partitions containing the value `success` in the status field. 

  6. Event Result set.




### Summary and Results

The query is used to detect event A happening X times before event B within a specific timespan. It looks for instances where there were 3 or more failed attempts followed by a successful attempt, all occurring within a 3-second window. Using a sliding time window of 3 seconds, provides a more precise time constraint compared to the usage of [`partition()`](https://library.humio.com/data-analysis/functions-partition.html) in [Detect Event A Happening X Times Before Event B](examples-partition-groupby-detect-event-a.html "Detect Event A Happening X Times Before Event B"). 

The query can be used to detect potential brute force attack patterns within a specific timeframe. Note that the effectiveness of this query depends on the nature of your data and the typical patterns in your system. 

Sample output from the incoming example data: 

key| failures| status  
---|---|---  
a| 5| success  
a| 7| success
