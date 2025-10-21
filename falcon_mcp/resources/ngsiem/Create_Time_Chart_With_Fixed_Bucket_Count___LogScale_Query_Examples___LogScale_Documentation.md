# Create Time Chart With Fixed Bucket Count | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timechart-method-buckets.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Time Chart With Fixed Bucket Count

Create a time chart with precise bucket control to visualize HTTP Methods Distribution using [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    timeChart(buckets=10, series=method, function=count())

### Introduction

The [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function can be used to create time-based visualizations of data. Instead of specifying a time span, you can control the granularity by setting the exact number of buckets to divide the time range into. 

In this example, the [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function is used to create a time series visualization showing the distribution of HTTP methods across exactly 10 time buckets. 

Example incoming data might look like this: 

@timestamp| method| url| status_code| response_time  
---|---|---|---|---  
2025-08-06T10:00:00Z| GET| /api/users| 200| 45  
2025-08-06T10:00:01Z| POST| /api/orders| 201| 120  
2025-08-06T10:00:02Z| GET| /api/products| 200| 35  
2025-08-06T10:00:03Z| PUT| /api/users/123| 200| 89  
2025-08-06T10:00:04Z| DELETE| /api/orders/456| 200| 67  
2025-08-06T10:00:05Z| GET| /api/inventory| 200| 56  
2025-08-06T10:00:06Z| POST| /api/users| 201| 98  
2025-08-06T10:00:07Z| GET| /api/orders| 200| 43  
2025-08-06T10:00:08Z| PATCH| /api/products/789| 200| 76  
2025-08-06T10:00:09Z| GET| /api/status| 200| 23  
2025-08-06T10:00:10Z| HEAD| /api/health| 200| 12  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timeChart(buckets=10, series=method, function=count())

Creates a time chart that divides the query time range into exactly 10 equal-width buckets. 

The [_`series`_](https://library.humio.com/data-analysis/functions-timechart.html#query-functions-timechart-series) parameter groups the data by the [method](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html) field, creating separate lines for each unique HTTP method. 

The [_`function`_](https://library.humio.com/data-analysis/functions-timechart.html#query-functions-timechart-function) parameter uses [`count()`](https://library.humio.com/data-analysis/functions-count.html) to calculate the number of events in each bucket. 

Using [_`buckets`_](https://library.humio.com/data-analysis/functions-timechart.html#query-functions-timechart-buckets) instead of a time span ensures consistent granularity regardless of the total time range, making the visualization more predictable and easier to compare across different time ranges. For an example, see [Create Time Chart With One-Minute Intervals](examples-timechart-span-minutes.html "Create Time Chart With One-Minute Intervals"). 

  3. Event Result set.




### Summary and Results

The query is used to create a detailed time series visualization showing how the usage of different HTTP methods varies over time, with precise control over the number of data points. 

This query is useful, for example, to analyze API usage patterns, detect unusual spikes in specific HTTP methods, or monitor the distribution of request types with consistent granularity regardless of the time range. 

If you want to create a time series visualization showing the distribution of HTTP methods within the [HUMIO](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository, you can use these queries: `#kind=requests | timeChart(buckets=10, series=method, function=count())` or just `#kind=requests | timeChart(series=method, function=count())`. 

When the [_`buckets`_](https://library.humio.com/data-analysis/functions-timechart.html#query-functions-timechart-buckets) parameter is not specified, LogScale automatically determines an appropriate number of buckets based on the query time range. This ensures optimal visualization regardless of the time span being analyzed. 

Sample time chart from the incoming example data will look like this: 

![Showing Time Chart With Fixed Bucket Count](images/timechart-bucket-span-method.png)  
---  
  
Note that each HTTP method gets its own column, and the _bucket column represents the start of each time bucket. The values show the count of each method within that bucket.
