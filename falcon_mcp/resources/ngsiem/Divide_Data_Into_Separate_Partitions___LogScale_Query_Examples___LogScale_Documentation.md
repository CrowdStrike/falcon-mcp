# Divide Data Into Separate Partitions | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-partition-count.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Divide Data Into Separate Partitions

Divide data into separate partitions based on a specific condition using the [`partition()`](https://library.humio.com/data-analysis/functions-partition.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    head()
    | partition(count(), condition=test(splitHere))

### Introduction

The [`partition()`](https://library.humio.com/data-analysis/functions-partition.html) function can be used to group related events together and perform calculations within each partition separately. The [`partition()`](https://library.humio.com/data-analysis/functions-partition.html) function analyzes data, and when it finds data that meets the specified condition, it creates a new group applying the chosen calculation (for example, [`count()`](https://library.humio.com/data-analysis/functions-count.html) or [`sum()`](https://library.humio.com/data-analysis/functions-sum.html)) to each group independently. 

In this example, the [`partition()`](https://library.humio.com/data-analysis/functions-partition.html) function is used with the [`head()`](https://library.humio.com/data-analysis/functions-head.html) function to count the number of events in each group, starting a new count whenever the field splitHere is `true`. 

Note that the [`partition()`](https://library.humio.com/data-analysis/functions-partition.html) function must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

splitHere  
---  
false  
false  
false  
true  
false  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head()

Selects the oldest events ordered by time. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | partition(count(), condition=test(splitHere))

Splits the events (creates a new subsequence) whenever the splitHere field is `true` and counts the number of events in each partition (group), returning the results in a field named _count. 

For example, if you have five events and the third one has the field splitHere as `true`, two groups are created: 

     * **Group 1:** 3 events (including the "true" point) 

     * **Group 2:** 2 events 

Note that it is possible to split after the event, where the condition is `true`: 

logscale
    
    partition(count(), condition=test(splitHere), split=after)

. 
  4. Event Result set.




### Summary and Results

The query is used to split a sequence of events into multiple partitions based on a conditional test. 

Sample output from the incoming example data: 

_count  
---  
3  
2  
  
Sample output from the incoming example data if condition is true and split equals `after`: 

_count  
---  
4  
1  
  
The query is useful for grouping related events and performing calculations within these groups.
