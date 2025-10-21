# Create Time Chart Widget for All Events | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timechart-count.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Time Chart Widget for All Events

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    timeChart(span=1h, function=count())

### Introduction

The [Time Chart](https://library.humio.com/data-analysis/widgets-timechart.html) is the most commonly used widget in LogScale. It displays bucketed time series data on a timeline. The [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function is used to create time chart widgets, in this example a timechart that shows the number of events per hour over the last 24 hours. We do this by selecting to search over the last 24 hours in the time selector in the UI, and then we tell the function to make each time bucket one hour long (with`span=1hour`). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timeChart(span=1h, function=count())

Creates 24 time buckets when we search over the last 24 hours, and all searched events get sorted into groups depending on the bucket they belong to (based on their @timestamp  value). When all events have been divided up by time, the [`count()`](https://library.humio.com/data-analysis/functions-count.html) function is run on each group, giving us the number of events per hour. 

  3. Event Result set.




### Summary and Results

The query is used to create timechart widgets showing number of events per hour over the last 24 hours. The timechart shows one group of events per time bucket. When viewing and hovering over the buckets within the time chart, the display will show the precise value and time for the displayed bucket, with the time showing the point where the bucket starts.
