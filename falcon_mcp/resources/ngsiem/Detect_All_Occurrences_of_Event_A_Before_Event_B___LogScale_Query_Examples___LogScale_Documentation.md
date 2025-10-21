# Detect All Occurrences of Event A Before Event B | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-partition-groupby-detect-all-occurrences.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Detect All Occurrences of Event A Before Event B

Detect all occurrences of event A before event B (brute force attack) using the [`partition()`](https://library.humio.com/data-analysis/functions-partition.html) function combined with [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result

logscale
    
    
    head()
    | groupBy(
          key,
          function = partition(
              condition=test(status=="success"),
              split="after",
              [
                  { status="failure" | count(as=failures) }, 
                  range(@timestamp, as=timespan), 
                  selectLast(status)
              ]
          )
      )
    | failures >= 3
    | status = "success"

### Introduction

In this example, the [`partition()`](https://library.humio.com/data-analysis/functions-partition.html) function is used with the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function to detect all occurrences of event A before event B (brute force attack). 

The query will detect instances where there were 3 or more failed attempts followed by a successful attempt within the specified 10-second window. 

Note that the [`partition()`](https://library.humio.com/data-analysis/functions-partition.html) function must be used after an aggregator function to ensure event ordering. Also note that the events must be sorted in order by timestamp to prevent errors when running the query. It is possible to select any field to use as a timestamp. 

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

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head()

Selects the oldest events ordered by time. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy(
               key,
               function = partition(
                   condition=test(status=="success"),
                   split="after",
                   [
                       { status="failure" | count(as=failures) }, 
                       range(@timestamp, as=timespan), 
                       selectLast(status)
                   ]
               )
           )

Groups the events by a specified key (for example, a user ID or IP address), filters for successful events (filters for events that meet the defined condition for the field status that must contain the value `success`), then splits the data after each successful event. Notice how the condition is provided as a non-aggregate subquery. 

Furthermore, it filters all the failed attempts where the field status contains the value `failure`. 

Makes a count of all the failed attempts, and returns the results in a field named failures, calculates the timespan of the failures, and selects the status of the last event. Calculating the timespan of the failure sequence, is useful for analysis. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | failures >= 3

Filters for partitions with 3 or more failures. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | status = "success"

Filters for partitions containing the value `success` in the status field. 

  6. Event Result set.




### Summary and Results

The query is used to detect all occurrences of potential brute force attack patterns. It looks for instances where there were 3 or more failed attempts (event A) followed by a successful attempt (event B), regardless of the time between failures. The timespan between each attempt is reported, which could be used to identify brute force attacks. 

Sample output from the incoming example data: 

key| failures| timespan| status  
---|---|---|---  
a| 5| 1600| success  
a| 3| 300| success  
c| 3| 3100| success
