# Calculate Multiple Response Time Percentiles | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-percentile-response-times.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Multiple Response Time Percentiles

Calculate different percentiles for response time measurements using the [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    percentile(field=responsetime, percentiles=[50, 75, 99, 99.9])

### Introduction

The [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) function can be used to calculate specified percentile values from a set of numeric data, helping identify performance thresholds and outliers in the data distribution. 

In this example, the [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) function is used to calculate multiple percentiles (50th, 75th, 99th, and 99.9th) of response times to analyze performance distribution. 

Example incoming data might look like this: 

@timestamp| service_name| responsetime| status_code  
---|---|---|---  
2023-06-15T10:00:00Z| api_gateway| 45| 200  
2023-06-15T10:00:01Z| api_gateway| 62| 200  
2023-06-15T10:00:02Z| api_gateway| 89| 200  
2023-06-15T10:00:03Z| api_gateway| 123| 500  
2023-06-15T10:00:04Z| api_gateway| 234| 200  
2023-06-15T10:00:05Z| api_gateway| 56| 200  
2023-06-15T10:00:06Z| api_gateway| 78| 200  
2023-06-15T10:00:07Z| api_gateway| 345| 503  
2023-06-15T10:00:08Z| api_gateway| 67| 200  
2023-06-15T10:00:09Z| api_gateway| 89| 200  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         percentile(field=responsetime, percentiles=[50, 75, 99, 99.9])

Calculates four different percentiles of the responsetime field: 

     * 50th percentile (median) 

     * 75th percentile (third quartile) 

     * 99th percentile (common SLA threshold) 

     * 99.9th percentile (extreme outlier threshold) 

The [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) function returns the results in new fields named responsetime_50, responsetime_75, responsetime_99, and responsetime_99.9. 

  3. Event Result set.




### Summary and Results

The query is used to analyze the distribution of response times and identify performance thresholds. 

This query is useful, for example, to establish SLA thresholds, identify performance bottlenecks, or monitor service performance over time. 

Sample output from the incoming example data: 

responsetime_50| responsetime_75| responsetime_99| responsetime_99.9  
---|---|---|---  
78| 123| 345| 345
