# Show Percentiles Across Multiple Buckets | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-buckets-percentile.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Show Percentiles Across Multiple Buckets

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    bucket(span=60sec, function=percentile(field=responsetime, percentiles=[50, 75, 99, 99.9]))

### Introduction

Show response time percentiles over time. Calculate percentiles per minute by bucketing into 1 minute intervals: 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         bucket(span=60sec, function=percentile(field=responsetime, percentiles=[50, 75, 99, 99.9]))

Using a 60 second timespan for each bucket, displays the [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) for the responsetime field. 

  3. Event Result set.




### Summary and Results

The [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) quantifies values by determining whether the value is larger than a percentage of the overall values. The output provides a powerful view of the relative significance of a value. Combined in this example with [`bucket()`](https://library.humio.com/data-analysis/functions-bucket.html), the query will generate buckets of data showing the comparative response time for every 60 seconds.
