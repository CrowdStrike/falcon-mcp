# Count Events Within Partitions Based on Condition | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-partition-neighbor-accumulation-example.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Count Events Within Partitions Based on Condition

Count events within partitions based on a specific condition using the [`partition()`](https://library.humio.com/data-analysis/functions-partition.html) function combined with [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) and [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    head()
    | neighbor(key, prefix=prev)
    | partition(accumulate(count()), condition=test(key != prev.key))

### Introduction

Accumulations can be partitioned based on a condition, such as a change in value. This is achieved by combining the three functions [`partition()`](https://library.humio.com/data-analysis/functions-partition.html), [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) and [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html). In this example, the combination of the 3 sequence functions is used to count events within partitions defined by changes in a key field. 

Note that sequence functions must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

key  
---  
a  
a  
a  
b  
a  
b  
b  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head()

Selects the oldest events ordered by time. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | neighbor(key, prefix=prev)

Accesses the value in the field key from the previous event. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | partition(accumulate(count()), condition=test(key != prev.key))

The [`partition()`](https://library.humio.com/data-analysis/functions-partition.html) function splits the sequence of events based on the specified condition. A new partition starts when the current key value is different from the previous key value. Within each partition, it counts the number of events, and returns the results in a field named _count. 

  5. Event Result set.




### Summary and Results

The query is used to compute an accumulated count of events within partitions based on a specific condition, in this example change in value for the field key. 

Sample output from the incoming example data: 

key| _count| prev.key  
---|---|---  
a| 1| <no value>  
a| 2| a  
a| 3| a  
b| 1| a  
a| 1| b  
b| 1| a  
b| 2| b  
  
The query is useful for analyzing sequences of events, especially when you want to identify and count consecutive occurrences of a particular attribute in order to identify and analyze patterns or sequences within your data.
