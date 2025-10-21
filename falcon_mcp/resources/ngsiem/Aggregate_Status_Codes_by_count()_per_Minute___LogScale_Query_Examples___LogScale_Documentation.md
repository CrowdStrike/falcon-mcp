# Aggregate Status Codes by count() Per Minute | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-bucket-statuscodes.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Aggregate Status Codes by [`count()`](https://library.humio.com/data-analysis/functions-count.html) Per Minute

Time series aggregate status codes by [`count()`](https://library.humio.com/data-analysis/functions-count.html) per minute into buckets 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    bucket(1min, field=status_code, function=count())

### Introduction

Bucketing is a powerful technique for optimizing data storage and query performance. Bucketing allows for data to be collected according to a time range, dividing large datasets into manageable parts, thereby making it easier to quickly find specific events. 

In this example, the [`bucket()`](https://library.humio.com/data-analysis/functions-bucket.html) function is used with [`count()`](https://library.humio.com/data-analysis/functions-count.html) to count different HTTP status codes over time and bucket them into time intervals of 1 minute. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         bucket(1min, field=status_code, function=count())

Counts different HTTP status codes over time and buckets them into time intervals of 1 minute. Notice that we group by two fields: status_code field and the implicit field _bucket. 

  3. Event Result set.




### Summary and Results

The query is used to optimizing data storage and query performance. Bucketing allows for data to be collected according to a time range. Using the right aggregation function to quantify the value groups that information into the buckets suitable for graphing for example with a [`Bar Chart`](https://library.humio.com/data-analysis/widgets-barchart.html), with the size of the bar using the declared function result, [`count()`](https://library.humio.com/data-analysis/functions-count.html) in this example.
