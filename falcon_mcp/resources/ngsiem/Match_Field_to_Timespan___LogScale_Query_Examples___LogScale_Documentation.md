# Match Field to Timespan | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-eval-timespan.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Match Field to Timespan

Match a field to timespan using the [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function with [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    timechart(method, span=5min)
    | eval(_count=_count/5)

### Introduction

The [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function can be used to create new or update existing fields. 

In this example, the [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function is used with [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) to match a field to the timespan, dividing the count by 5 to convert from a 5 minute count to a per-minute count. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timechart(method, span=5min)

Creates a timechart based on the values of the method field, and groups data into 5 minute buckets (span=5min). By default, it counts events in each bucket and returns the result in a field named _count. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | eval(_count=_count/5)

Divides the count by 5 to convert from a 5-minute count to a per-minute count, and returns the new value in the _count field. 

This approach is useful when you want to display per-minute rates but also want to benefit from the reduced data points and improved performance of larger time buckets. 

  4. Event Result set.




### Summary and Results

The query is used to match a field to a timespan. It summarizes the count into 5 minutes blocks and then displays those using the [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html)_`timespan`_ parameter to display the value in those increments. 

The [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function then summarizes the values by dividing the 5 minutes counts by 5 to provide a summarized value for each 5 minutes timespan. You can, for example, use it to test a complex function or expression with different inputs and quickly check the output in the returned values.
