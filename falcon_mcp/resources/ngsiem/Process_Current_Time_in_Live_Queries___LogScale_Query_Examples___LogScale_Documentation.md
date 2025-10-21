# Process Current Time in Live Queries | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-now-current-time-livequeries.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Process Current Time in Live Queries

Process current time in live queries using the [`now()`](https://library.humio.com/data-analysis/functions-now.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    curr := now()

### Introduction

The now() function is used in live queries to process the current time for each event. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         curr := now()

Processes current time for each event and returns the timestamps in a field named curr field. It records when events occur. The timestamp represents milliseconds. 

  3. Event Result set.




### Summary and Results

The query is used in live queries to process the current time for each event. 

Note that in live queries, this query returns timestamps based on the [`now()`](https://library.humio.com/data-analysis/functions-now.html) function's location: 

  * Before first aggregate function: Returns the initial event processing timestamp (it is only evaluated the first time the query sees the event). 

  * After first aggregate function: Returns continuously updated timestamps from each LogScale node (it gives the live value of the current system time, which can divert between LogScale nodes when [`now()`](https://library.humio.com/data-analysis/functions-now.html) is placed after the first aggregate function). 




The [`now()`](https://library.humio.com/data-analysis/functions-now.html) function and capturing current timestamps is, for example, useful in security contexts for incident response timing, threat detection timestamps and security event correlation.
