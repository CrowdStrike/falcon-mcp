# Create Time Chart With Default Percentiles For Multiple Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timechart-default-percentiles-multiple-fields.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Time Chart With Default Percentiles For Multiple Fields

Visualize default percentiles (50th, 75th, 99th) of two metrics over time using the [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) function with [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    timeChart(function=[percentile(field=r1,as=r1),percentile(field=r2,as=r2)], span=4m)

### Introduction

The [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function combined with the [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) function can be used to analyze and visualize how different metrics' distributions change over time. 

When [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) is used without specifying percentiles, it automatically calculates three default percentiles (50th, 75th, and 99th) for the given field. 

In this example, the [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function combines with two [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) calculations to track the distribution of two different metrics (r1 and r2) over time. 

Note that when [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) is used without specifying percentiles, it automatically calculates three default percentiles (50th, 75th, and 99th) for the given field. 

Example incoming data might look like this: 

@timestamp| service| r1| r2| status  
---|---|---|---|---  
2023-06-15T10:00:00Z| service_a| 120| 150| ok  
2023-06-15T10:01:00Z| service_a| 145| 165| ok  
2023-06-15T10:02:00Z| service_a| 98| 110| ok  
2023-06-15T10:03:00Z| service_a| 167| 190| error  
2023-06-15T10:04:00Z| service_a| 134| 155| ok  
2023-06-15T10:05:00Z| service_a| 178| 195| ok  
2023-06-15T10:06:00Z| service_a| 143| 160| ok  
2023-06-15T10:07:00Z| service_a| 156| 175| ok  
2023-06-15T10:08:00Z| service_a| 289| 310| error  
2023-06-15T10:09:00Z| service_a| 123| 145| ok  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timeChart(function=[percentile(field=r1,as=r1),percentile(field=r2,as=r2)], span=4m)

Creates a time chart with timespan of 4 minutes per bucket showing three percentile values for each field: 

     * For field r1, creates: 

       * r1_50 (median) 

       * r1_75 (third quartile) 

       * r1_99 (99th percentile) 

     * For field r2, creates: 

       * r2_50 (median) 

       * r2_75 (third quartile) 

       * r2_99 (99th percentile) 

The [_`span`_](https://library.humio.com/data-analysis/functions-timechart.html#query-functions-timechart-span) parameter is used to define the timespan of the bucket. 

  3. Event Result set.




### Summary and Results

The query produces a time series showing the distribution of both metrics using three different percentile thresholds, allowing for comprehensive performance analysis. When percentiles are not explicitly specified, the [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) function automatically calculates three default percentiles (50th, 75th, and 95th). 

This query is useful for comparing typical (median) performance between two metrics, identifying performance variations using the 75th percentile and monitoring extreme outliers with the 99th percentile 

Sample output from the incoming example data: 

_bucket| r1_50| r1_75| r1_99| r2_50| r2_75| r2_99  
---|---|---|---|---|---|---  
1.68682E+12| 120.80792246242098| 143.93947040702542| 143.93947040702542| 149.4847016559383| 163.94784285493662| 163.94784285493662  
1.68682E+12| 143.93947040702542| 155.16205054702775| 155.16205054702775| 160.9814359681496| 176.22889949490784| 176.22889949490784  
1.68682E+12| 123.13088804780689| 123.13088804780689| 123.13088804780689| 143.93947040702542| 143.93947040702542| 143.93947040702542  
  
Note that the different buckets contain six different percentile values, three for each metric. The 99th percentile captures the extreme values in the data, making it useful for identifying outliers and performance anomalies. 

![Showing Default Percentiles of Two Metrics](images/timechart-percentile-multi-fields.png)  
---
