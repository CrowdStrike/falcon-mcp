# Compute Cumulative Aggregation For Specific Group  | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-accumulate-groupby-example.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Compute Cumulative Aggregation For Specific Group 

Compute a cumulative aggregation for a specific group using the [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function with [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    head()
    | groupBy(key, function = accumulate(sum(value)))

### Introduction

The [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function can be used to calculate running totals, averages, or other cumulative metrics over time or across a series of events. The [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function applies an aggregation function cumulatively to a sequence of events. 

In this example, to compute a cumulative aggregation for a specific group (for example, by user), the [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function is used inside the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function. 

Note that the [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

key| value  
---|---  
a| 5  
b| 6  
a| 1  
c| 2  
b| 6  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head()

Selects the oldest events ordered by time. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy(key, function = accumulate(sum(value)))

Accumulates the sum of a field named value, groups the data by a specified key and returns the results in a field named _sum. 

  4. Event Result set.




### Summary and Results

The query is used to compute a cumulative aggregation for a specific group, in this example using the value field. 

Sample output from the incoming example data: 

key| _sum| value  
---|---|---  
a| 5| 5  
a| 6| 1  
b| 6| 6  
b| 12| 6  
c| 2| 2
