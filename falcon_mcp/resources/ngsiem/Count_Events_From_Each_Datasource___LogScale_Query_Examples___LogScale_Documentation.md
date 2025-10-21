# Count Events From Each Datasource
     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-eventinternals-number.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Count Events From Each Datasource 

Count events from each datasource by using [`eventInternals()`](https://library.humio.com/data-analysis/functions-eventinternals.html) function to add storage location to each event 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    eventInternals()
    | groupBy([@datasourceId])

### Introduction

The [`eventInternals()`](https://library.humio.com/data-analysis/functions-eventinternals.html) function is used to add the storage locations of this event. The [`eventInternals()`](https://library.humio.com/data-analysis/functions-eventinternals.html) function augments the event data with the event field count information. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         eventInternals()

Adds a @datasourceId field describing the storage locations of the event. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy([@datasourceId])

Groups the events based on the @datasourceId, performs a count of the events and returns the results in a _count field. 

  4. Event Result set.




### Summary and Results

The query is used to find the number of events per datasource.
