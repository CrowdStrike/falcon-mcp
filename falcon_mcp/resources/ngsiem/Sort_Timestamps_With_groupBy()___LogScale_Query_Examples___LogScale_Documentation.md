# Sort Timestamps With groupBy()

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-groupby-sort-timestamps.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Sort Timestamps With [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html)

Sorting fields based on aggregated field values 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2{{Aggregate}} 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

**Search Repository:** [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html)

logscale
    
    
    timestamp := formatTime(format="%H:%M")
    | groupBy([thread],
    function=[{sort("timestamp")
    | collect("timestamp")}])

### Introduction

When using aggregation, you may want to sort on a field that is part of the aggregated set but not the main feature of the aggregated value. For example, sorting the values by their timestamp rather than the embedded value. To achieve this, you should use a function that sorts the field to be used as the sort field, and then use [`collect()`](https://library.humio.com/data-analysis/functions-collect.html) so that the value from before the aggregation can be displayed in the generated event set. This query can be executed in the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) respository. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2{{Aggregate}} 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timestamp := formatTime(format="%H:%M")

Creates a new field, timestamp formatted as `HH:MM`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2{{Aggregate}} 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy([thread],

Groups the events, first by the name of the thread and then the formatted timestamp. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2{{Aggregate}} 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         function=[{sort("timestamp")
         | collect("timestamp")}])

Uses the [`sort()`](https://library.humio.com/data-analysis/functions-sort.html) combined with [`collect()`](https://library.humio.com/data-analysis/functions-collect.html) as the method fo aggregation. As an embedded expression for the function, this will sort the events on the timestamp field and then retrieve the field as it would normally be removed as part of the aggregation process. 

  5. Event Result set.




### Summary and Results

The result set will contain a list of the aggregated thread names sorted by the timestamp: 

thread| timestamp  
---|---  
BootstrapInfoJob| 10:09  
DataSynchJob| 10:09  
Global event loop| 10:10  
LocalLivequeryMonitor| 10:09  
LogCollectorManifestUpdate| 10:09  
TransientChatter event loop| 10:10  
aggregate-alert-job| 10:09  
alert-job| 10:09  
block-processing-monitor-job| 10:09  
bloom-scheduler| 10:09  
bucket-entity-config| 10:09  
bucket-overcommit-metrics-job| 10:09  
bucket-storage-download| 10:09  
bucket-storage-prefetch| 10:09  
chatter-runningqueries-logger| 10:09  
chatter-runningqueries-stats| 10:09
