# Create Time Chart With One-Minute Intervals | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timechart-span-minutes.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Time Chart With One-Minute Intervals

Analyze request methods in fixed one-minute buckets using the [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    timeChart(span=1min, series=method, function=count())

### Introduction

The [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function can be used to create time-based visualizations by grouping events into fixed time intervals specified using the [_`span`_](https://library.humio.com/data-analysis/functions-timechart.html#query-functions-timechart-span) parameter. 

In this example, the [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function is used with the [_`span`_](https://library.humio.com/data-analysis/functions-timechart.html#query-functions-timechart-span) parameter to create a time series visualization showing the count of HTTP request methods aggregated into one-minute intervals. 

Example incoming data might look like this: 

@timestamp| method| path| status_code| response_time  
---|---|---|---|---  
2025-08-06T10:00:15Z| GET| /api/users| 200| 45  
2025-08-06T10:00:45Z| POST| /api/users| 201| 78  
2025-08-06T10:01:12Z| GET| /api/products| 200| 32  
2025-08-06T10:01:38Z| PUT| /api/users/1| 200| 65  
2025-08-06T10:02:05Z| DELETE| /api/users/2| 204| 28  
2025-08-06T10:02:30Z| GET| /api/orders| 200| 52  
2025-08-06T10:03:18Z| POST| /api/orders| 201| 89  
2025-08-06T10:03:42Z| GET| /api/products| 200| 41  
2025-08-06T10:04:15Z| PUT| /api/orders/1| 200| 67  
2025-08-06T10:04:55Z| GET| /api/users| 200| 38  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timeChart(span=1min, series=method, function=count())

Creates a time series chart by grouping events into fixed one-minute intervals using [_`span=1min`_](https://library.humio.com/data-analysis/functions-timechart.html#query-functions-timechart-span)

The [_`series`_](https://library.humio.com/data-analysis/functions-timechart.html#query-functions-timechart-series) parameter groups the data by the [method](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html) field, creating separate lines for each unique HTTP method. 

The [_`function`_](https://library.humio.com/data-analysis/functions-timechart.html#query-functions-timechart-function) parameter uses [`count()`](https://library.humio.com/data-analysis/functions-count.html) to calculate the number of events in each minute interval for each method. 

The [_`span`_](https://library.humio.com/data-analysis/functions-timechart.html#query-functions-timechart-span) parameter creates fixed-width time buckets, ensuring consistent interval sizes regardless of the query time range. This differs from using [_`buckets`_](https://library.humio.com/data-analysis/functions-timechart.html#query-functions-timechart-buckets), which divides the total time range into a specified number of intervals. For an example, see [Create Time Chart With Fixed Bucket Count](examples-timechart-method-buckets.html "Create Time Chart With Fixed Bucket Count"). 

  3. Event Result set.




### Summary and Results

The query is used to analyze the precise per-minute distribution of HTTP request methods, providing fixed time interval analysis. 

This query is useful, for example, to monitor minute-by-minute API usage patterns, detect short-term spikes in specific request methods and analyze request patterns with consistent time granularity 

If you want to create a time series visualization showing the distribution of HTTP methods within the [HUMIO](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository, you can use this query:`#kind=requests | timeChart(span=1min, series=method, function=count())`

Sample time chart from the incoming example data will look like this: 

![Showing Time Chart With One-Minute Intervals](images/timechart-one-min-span-method.png)  
---  
  
Note that events are grouped into the minute they occurred in, regardless of the specific seconds.
