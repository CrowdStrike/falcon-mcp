# Convert Timestamps Based on Accuracy | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-if-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Convert Timestamps Based on Accuracy

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    errortime := if((@ingesttimestamp > @timestamp), then=@timestamp, else=@ingesttimestamp) / 1000

### Introduction

When parsing and processing data, the time of the data can be critical, and not all events include an explicit @timestamp field, but the ingest time stamp, when the event was parsed by LogScale, can be a suitable proxy. The lack of timestamp, or a significant difference between the timestamps may result in displaying an empty value (or creating an event stream that cannot be summarized in a graph). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         errortime := if((@ingesttimestamp > @timestamp), then=@timestamp, else=@ingesttimestamp) / 1000

The event field errortime is set to the latest time value, either timestamp or @ingesttimestamp. 

  3. Event Result set.




### Summary and Results

Selecting time by the accuracy allows for incoming data to be of different time accuracy but still return consistent results.
