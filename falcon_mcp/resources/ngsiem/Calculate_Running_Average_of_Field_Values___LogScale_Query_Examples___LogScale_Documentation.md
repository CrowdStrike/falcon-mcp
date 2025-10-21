# Calculate Running Average of Field Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-accumulate-basic.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Running Average of Field Values

Calculate a running average of values in a dataset using the [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    head()
    | accumulate(avg(value))

### Introduction

The [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function can be used to calculate running totals, averages, or other cumulative metrics over time or across a series of events. The [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function applies an aggregation function cumulatively to a sequence of events. 

In this example, the [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function is used with the [`avg()`](https://library.humio.com/data-analysis/functions-avg.html) function to calculate a running average of the field value. 

Note that the [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function must be used after an aggregator function, in this example the [`head()`](https://library.humio.com/data-analysis/functions-head.html) function, to ensure event ordering. 

Example incoming data might look like this: 

key| value  
---|---  
a| 5  
b| 6  
c| 1  
d| 2  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head()

Ensures that the events are ordered by time, selecting the oldest events. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | accumulate(avg(value))

Computes the running average of all values, including the current one, using the [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function with the [`avg()`](https://library.humio.com/data-analysis/functions-avg.html) aggregator. 

  4. Event Result set.




### Summary and Results

The query is used to calculate the running average of fields. The query calculates moving averages that change as new values arrive. 

Sample output from the incoming example data: 

_avg| key| value  
---|---|---  
5| a| 5  
5.5| b| 6  
4| c| 1  
3.5| d| 2
