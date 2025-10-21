# Create Time Chart Widget for Different Events | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timechart-different-events.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Time Chart Widget for Different Events

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    timeChart(span=1h, function=count(), series=method)

### Introduction

The [Time Chart](https://library.humio.com/data-analysis/widgets-timechart.html) is the most commonly used widget in LogScale. It displays bucketed time series data on a timeline. The [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function is used to create time chart widgets, in this example a timechart that shows the number of the different events per hour over the last 24 hours. For example, you may want to count different kinds of HTTP methods used for requests in the logs. If those are stored in a field named method, you can use this field as a `series`. Furthermore, we select to search over the last 24 hours in the time selector in the UI, and also add a function to make each time bucket one hour long (with`span=1hour`). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timeChart(span=1h, function=count(), series=method)

Creates 24 time buckets when we search over the last 24 hours, and all searched events get sorted into groups depending on the bucket they belong to (based on their @timestamp  value). When all events have been divided up by time, the [`count()`](https://library.humio.com/data-analysis/functions-count.html) function is run on the series field to return the number of each different kinds of events per hour. 

  3. Event Result set.




### Summary and Results

The query is used to create timechart widgets showing number of different kinds of events per hour over the last 24 hours. In this example we do not just have one group of events per time bucket, but multiple groups: one group for every value of method that exists in the timespan we are searching in. So if we are still searching over a 24 hour period, and we have received only `GET`, `PUT`, and `POST` requests in that timespan, we will get three groups of events per bucket (because we have three different values for method) Therefore, we end up with 72 groups of events. And every group contains only events which correspond to some time bucket and a specific value of method. Then [`count()`](https://library.humio.com/data-analysis/functions-count.html) is run on each of these groups, to give us the number of `GET` events per hour, `PUT` events per hour, and `POST` events per hour. When viewing and hovering over the buckets within the time chart, the display will show the precise value and time for the displayed bucket, with the time showing the point where the bucket starts.
