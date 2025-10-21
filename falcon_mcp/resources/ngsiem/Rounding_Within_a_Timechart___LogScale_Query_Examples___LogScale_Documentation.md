# Rounding Within a Timechart | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-functions-round-floor.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Rounding Within a Timechart

Round down a number in a field and display information in a timechart using the [`round()`](https://library.humio.com/data-analysis/functions-round.html) and [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) functions 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    timeChart(function={max(value) | round(_max, how=floor)})timechart(function=max(value))

### Introduction

When using the [`round()`](https://library.humio.com/data-analysis/functions-round.html) function in LogScale, a floating point number is rounded to the nearest integer. Using the _`floor`_ parameter to a function always rounds down a number. 

In this example, the [`round()`](https://library.humio.com/data-analysis/functions-round.html) function is used with a _`floor`_ parameter to round down a field value to an integer (whole number) and display information within a timechart. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timeChart(function={max(value) | round(_max, how=floor)})timechart(function=max(value))

Creates a time chart using [`max()`](https://library.humio.com/data-analysis/functions-max.html) as the aggregate function for a field named value to find the highest value in each time bucket, and returns the result in a field named _max. 

Rounds the implied field _max from the aggregate [`max()`](https://library.humio.com/data-analysis/functions-max.html) using the `floor` option to round down the value. 

Example of original _max values: `10.8`, `15.3`, `20.7`. 

After floor: `10`, `15`, `20`. 

  3. Event Result set.




### Summary and Results

The query is used to round down maximum values over time to nearest integer (whole value). This is useful when displaying information in a time chart. Rounding to nearest integer will make it easier to distinguish the differences between values when used on a graph for time-based visualization. The query simplifies the data presentation. 

### Note

To round to a specific decimal accuracy, the [`format()`](https://library.humio.com/data-analysis/functions-format.html) function must be used. 

![Showing Round with timeChart\(\)](images/timechart-round-max.png)  
---
