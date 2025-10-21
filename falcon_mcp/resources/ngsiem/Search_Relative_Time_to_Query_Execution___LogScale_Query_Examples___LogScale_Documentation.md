# Search Relative Time to Query Execution | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-relative-time.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Search Relative Time to Query Execution

Writing a query that is executed against a time range relative to when the query is executed using the [`start()`](https://library.humio.com/data-analysis/functions-start.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ffbf00;

logscale
    
    
    test(@timestamp < (start() + (30*24*60*60*1000)))

### Introduction

The [`start()`](https://library.humio.com/data-analysis/functions-start.html) function can be used in a query that executes against a time range relative to when the query is executed. 

In this example, the` start()` function is used to test if the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field is less than (earlier than) the start time plus `30` days. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ffbf00; style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         test(@timestamp < (start() + (30*24*60*60*1000)))

Tests whether the @timestamp for an event is less than the start time of the query. The query start time is returned by the [`start()`](https://library.humio.com/data-analysis/functions-start.html) function. 

To work out the relative time, we add the explicit number of milliseconds by calculating the number of milliseconds in the specified number of days, in this case, `30`. 

Time calculation breakdown is as follows: 

30 (days) 

× 24 (hours) 

× 60 (minutes) 

× 60 (seconds) 

× 1000 (milliseconds) 

= 2,592,000,000 milliseconds (30 days) 

  3. Event Result set.




### Summary and Results

The query is used to filter events that occurred within the first 30 days after the start time. 

The query is a practical way of querying with a relative time from the query execution. The 30 days (and calculation) used in the example could be updated with any time calculation to achieve the required result.
