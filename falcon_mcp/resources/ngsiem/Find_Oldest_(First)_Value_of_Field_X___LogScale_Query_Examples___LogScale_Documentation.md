# Find Oldest (First) Value of Field X | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-selectfrommin-lowest-value.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Oldest (First) Value of Field X

Find the oldest (first) value of field X using the [`selectFromMin()`](https://library.humio.com/data-analysis/functions-selectfrommin.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    selectFromMin(@timestamp, include=[x, @timestamp])

### Introduction

The [`selectFromMin()`](https://library.humio.com/data-analysis/functions-selectfrommin.html) function can be used to select a single event based on the minimum value of a specified field 

In this example, the [`selectFromMin()`](https://library.humio.com/data-analysis/functions-selectfrommin.html) function is used to find the oldest (first) value of the field x and return the timestamp when that value was recorded. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         selectFromMin(@timestamp, include=[x, @timestamp])

Sorts all events by timestamp, then selects the event in field x with the oldest (lowest) timestamp, returning only the specified fields x and @timestamp. 

In this example, [`selectFromMin()`](https://library.humio.com/data-analysis/functions-selectfrommin.html) filters for the "minimum value" of @timestamp, and finds the event with the oldest/first timestamp in the event set that also contains the specified field x. Timestamps are typically stored as numerical values (often in Unix epoch format), where lower numbers represent older times. 

The [_`include`_](https://library.humio.com/data-analysis/functions-selectfrommin.html#query-functions-selectfrommin-include) parameter is used to specify which fields to include in the output. 

  3. Event Result set.




### Summary and Results

The query is used to find the oldest value of field x by selecting the event with the lowest (oldest) timestamp value. 

Using this query is an efficient way to find the first value since it does not require sorting all results or using other aggregation functions - the query directly selects the oldest matching event.
