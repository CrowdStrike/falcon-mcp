# Calculate Median Memory Allocation | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-percentile-median-allocation.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Median Memory Allocation

Calculate the median (50th percentile) of memory allocations using the [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    percentile(field=allocBytes, percentiles=[50], as=median)

### Introduction

The [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) can be used to calculate the median value of a numeric field by specifying the 50th percentile, providing a measure of central tendency that is less sensitive to outliers than the mean. 

In this example, the [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) function is used to calculate the median of memory allocations by setting the 50th percentile and specifying a custom output field name. 

Example incoming data might look like this: 

@timestamp| process_name| allocBytes| thread_id  
---|---|---|---  
2023-06-15T10:00:00Z| java_app| 1024000| thread-1  
2023-06-15T10:00:01Z| java_app| 1548000| thread-2  
2023-06-15T10:00:02Z| java_app| 982000| thread-1  
2023-06-15T10:00:03Z| java_app| 2048000| thread-3  
2023-06-15T10:00:04Z| java_app| 1126000| thread-2  
2023-06-15T10:00:05Z| java_app| 1256000| thread-1  
2023-06-15T10:00:06Z| java_app| 1648000| thread-3  
2023-06-15T10:00:07Z| java_app| 3072000| thread-2  
2023-06-15T10:00:08Z| java_app| 1324000| thread-1  
2023-06-15T10:00:09Z| java_app| 1420000| thread-3  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         percentile(field=allocBytes, percentiles=[50], as=median)

Calculates the median (50th percentile) of the allocBytes field and returns the result in a new field named median_50 (the `_50` suffix is automatically added). 

  3. Event Result set.




### Summary and Results

The query is used to find the middle value (median) of memory allocations, providing a representative measure of typical allocation size. 

This query is useful, for example, to monitor typical memory usage patterns, establish baseline memory requirements, or detect changes in memory allocation behavior. 

Sample output from the incoming example data: 

median_50  
---  
1420000  
  
Note that the output field is automatically named median_50, combining the specified name with the percentile value.
