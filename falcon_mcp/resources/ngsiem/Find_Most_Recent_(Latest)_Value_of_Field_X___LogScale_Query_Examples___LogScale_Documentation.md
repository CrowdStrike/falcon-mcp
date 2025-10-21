# Find Most Recent (Latest) Value of Field X | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-selectfrommax-latest-value.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Most Recent (Latest) Value of Field X

Find the most recent (latest) value of field X using the [`selectFromMax()`](https://library.humio.com/data-analysis/functions-selectfrommax.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    selectFromMax(@timestamp, include=[x, @timestamp])

### Introduction

The [`selectFromMax()`](https://library.humio.com/data-analysis/functions-selectfrommax.html) function can be used to select a single event based on the maximum value of a specified field 

In this example, the [`selectFromMax()`](https://library.humio.com/data-analysis/functions-selectfrommax.html) function is used to find the most recent (latest) value of the field x and return the timestamp when that value was recorded. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         selectFromMax(@timestamp, include=[x, @timestamp])

Sorts all events by timestamp, then selects the event in field x with the highest (most recent) timestamp, returning only the specified fields x and @timestamp. 

In this example, [`selectFromMax()`](https://library.humio.com/data-analysis/functions-selectfrommax.html) filters for the "maximum value" of @timestamp, and finds the event with the newest/latest timestamp in the event set that also contains the specified field x. Timestamps are typically stored as numerical values (often in Unix epoch format), where larger numbers represent more recent times. 

The [_`include`_](https://library.humio.com/data-analysis/functions-selectfrommax.html#query-functions-selectfrommax-include) parameter is used to specify which fields to include in the output. 

  3. Event Result set.




### Summary and Results

The query is used to find the most recent value of field x by selecting the event with the highest (most recent) timestamp value. 

Using this query is an efficient way to find the latest value since it does not require sorting all results or using other aggregation functions - the query directly selects the most recent matching event.
