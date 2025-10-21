# Find Range Between Smallest And Largest Numbers in Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-range-value-responsetime.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

##  Find Range Between Smallest And Largest Numbers in Field

Find numeric range between the smallest and largest numbers in specified field using the [`range()`](https://library.humio.com/data-analysis/functions-range.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    range(responsetime)

### Introduction

A numeric range is the difference between the highest and lowest values in a specified numeric field across a set of events. The [`range()`](https://library.humio.com/data-analysis/functions-range.html) function can be used to calculate this difference and it works with both integer and floating-point fields. 

In this example, the [`range()`](https://library.humio.com/data-analysis/functions-range.html) function is used to find the range of the values in the field responsetime. 

Example incoming event data might look like this: 

timestamp| endpoint| responsetime  
---|---|---  
2025-04-30T07:00:00Z| /api/users| 0.125  
2025-04-30T07:00:01Z| /api/login| 2.543  
2025-04-30T07:00:02Z| /api/data| 0.891  
2025-04-30T07:00:03Z| /api/users| 1.234  
2025-04-30T07:00:04Z| /api/search| 3.456  
2025-04-30T07:00:05Z| /api/login| 0.567  
2025-04-30T07:00:06Z| /api/data| 1.789  
2025-04-30T07:00:07Z| /api/users| 0.234  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         range(responsetime)

Finds the range of the values in the field responsetime, and returns the result in a field named _range. The [`range()`](https://library.humio.com/data-analysis/functions-range.html) function always returns a single number (the difference between maximum and minimum). 

  3. Event Result set.




### Summary and Results

The query is used to calculate the difference between the highest and lowest values in the field responsetime across a set of events. Finding the range of responsetime in LogScale is particularly useful for performance analysis to identify performance inconsistancies. A small range indicates consistent performance, while a large range suggests reliability issues. 

The [`range()`](https://library.humio.com/data-analysis/functions-range.html) function is commonly used with [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) for comparative analysis. See [ Find Range of CPU Usage by Host](examples-range-groupby-cpu.html "Find Range of CPU Usage by Host"). 

Sample output from the incoming example data: 

_range  
---  
3.331
