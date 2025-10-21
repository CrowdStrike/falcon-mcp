# Deduplicate Content by Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-dedup.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Deduplicate Content by Field

Deduplicating content based on a specific field 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    groupBy(field, function=tail(1))

### Introduction

If you want to deduplicate events by a given field, for example to identify a unique list of events for further processing, you can use an aggregate function. In this example, the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function is used with [`tail()`](https://library.humio.com/data-analysis/functions-tail.html) to use the last value in a sequence of events. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(field, function=tail(1))

Groups all events in a specific field, and reduces the results using [`tail()`](https://library.humio.com/data-analysis/functions-tail.html) to take only the last value. 

  3. Event Result set.




### Summary and Results

The query is used to deduplicate events by a given field. This is useful if you want to create a unique list of events for further processing.
