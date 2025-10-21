# Make Data Compatible With Time Chart Widget - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-window-timechart-cpu-buckets.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Make Data Compatible With Time Chart Widget - Example 2

Make data compatible with [Time Chart](https://library.humio.com/data-analysis/widgets-timechart.html) using the [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function with [`window()`](https://library.humio.com/data-analysis/functions-window.html) and [_`buckets`_](https://library.humio.com/data-analysis/functions-window.html#query-functions-window-buckets) parameter 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    timeChart(host, function=window( function=[avg(cpu_load), max(cpu_load)], buckets=3))

### Introduction

The [Time Chart](https://library.humio.com/data-analysis/widgets-timechart.html) displays bucketed time series data on a timeline. The timeline shows the precise value and time for the displayed bucket, with the time showing the point where the bucket starts. The [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function is used to create the required input format for the time chart widget. Also the [`window()`](https://library.humio.com/data-analysis/functions-window.html) function is used to compute the running aggregate (for example, [`avg()`](https://library.humio.com/data-analysis/functions-avg.html) or [`sum()`](https://library.humio.com/data-analysis/functions-sum.html)) for a field over a sliding window of data in the time chart. 

Note that the [`window()`](https://library.humio.com/data-analysis/functions-window.html) function cannot be used elsewhere and with functions other than [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) or ` bucket()`. 

In this example, the [`window()`](https://library.humio.com/data-analysis/functions-window.html) function uses the number of buckets to calculate average and maximum CPU load. The timespan for each bucket will depend on the time interval of the query. The number of buckets are defined by the [_`buckets`_](https://library.humio.com/data-analysis/functions-window.html#query-functions-window-buckets) parameter. The [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function is used to create the required input format for the [Time Chart](https://library.humio.com/data-analysis/widgets-timechart.html). 

The query calculates both average AND maximum values across the requested timespan. In this example, the number of buckets is specified, so the events will be distributed across the specified number of buckets using a time span calculated from the time interval of the query. For example, a 15 minute time interval with 3 buckets would use a timespan of 5 minutes per bucket. 

### Note

The difference between [`window()`](https://library.humio.com/data-analysis/functions-window.html) and [`bucket()`](https://library.humio.com/data-analysis/functions-bucket.html) is that [`window()`](https://library.humio.com/data-analysis/functions-window.html) will create buckets with a consistent interval, whereas [`bucket()`](https://library.humio.com/data-analysis/functions-bucket.html) creates the buckets based on the query time. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timeChart(host, function=window( function=[avg(cpu_load), max(cpu_load)], buckets=3))

Groups by host, and calculates both the average of CPU load time and the maximum CPU load time (using aggregates ([`avg()`](https://library.humio.com/data-analysis/functions-avg.html) and [`max()`](https://library.humio.com/data-analysis/functions-max.html)) for the cpu_load field), displaying the results in 5 buckets showing a stacked graph for each host using a [Time Chart](https://library.humio.com/data-analysis/widgets-timechart.html). 

  3. Event Result set.




### Summary and Results

Selecting the number of buckets or the timespan of each bucket enables you to show a consistent view either by time or by number of buckets independent of the time interval of the query. For example, the widget could show 10 buckets whether displaying 15 minutes or 15 days of data; alternatively the display could always show the data for each 15 minutes. 

The query is used to make CPU load data compatible with the [Time Chart](https://library.humio.com/data-analysis/widgets-timechart.html). This query is, for example, useful for CPU load monitoring to compare intervals, compare hourly performance etc. 

For an example of dividing the input data by the timespan of each bucket, see [Make Data Compatible With Time Chart Widget - Example 1](examples-window-timechart-cpu.html "Make Data Compatible With Time Chart Widget - Example 1").
