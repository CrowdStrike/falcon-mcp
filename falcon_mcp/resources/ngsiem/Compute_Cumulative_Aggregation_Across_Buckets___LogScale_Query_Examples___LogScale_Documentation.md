# Compute Cumulative Aggregation Across Buckets | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-accumulate-bucket-example.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Compute Cumulative Aggregation Across Buckets

Compute a cumulative aggregation across buckets using the [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function with [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    timeChart(span=1000ms, function=sum(value))
    | accumulate(sum(_sum, as=_accumulated_sum))

### Introduction

The [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function can be used to calculate running totals, averages, or other cumulative metrics over time or across a series of events. The [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function applies an aggregation function cumulatively to a sequence of events. A common use case is to accumulate values across time intervals, such as days. This can be achieved by applying the [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function after a [`bucket()`](https://library.humio.com/data-analysis/functions-bucket.html) or [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function. 

In this example, the [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function is used with [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) to accumulate values across time intervals. 

Note that the [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) function must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

@timestamp| key| value  
---|---|---  
1451606301001| a| 5  
1451606301500| b| 6  
1451606301701| a| 1  
1451606302001| c| 2  
1451606302201| b| 6  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timeChart(span=1000ms, function=sum(value))

Groups data into 1-second buckets over a 4-second period, sums the field value for each bucket and returns the results in a field named _sum. The result is displayed in a timechart. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | accumulate(sum(_sum, as=_accumulated_sum))

Calculates a running total of the sums in the _sum field, and returns the results in a field named _accumulated_sum. 

  4. Event Result set.




### Summary and Results

The query is used to accumulate values across time intervals/buckets. The query is useful for tracking cumulative metrics or identifying trends in the data. 

Sample output from the incoming example data: 

_bucket| _sum| _accumulated_sum  
---|---|---  
1451606300000| 0| 0  
1451606301000| 12| 12  
1451606302000| 8| 20  
1451606303000| 0| 20  
  
The timechart looks like this: 

![Timechart displaying accumulated aggregation across buckets](images/timechart-accumulated-buckets.png)  
---
