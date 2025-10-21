# Find Minimum Value in Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-min-response-time-fast.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Minimum Value in Field

Calculate the minimum value in a numeric field using the [`min()`](https://library.humio.com/data-analysis/functions-min.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    min(responsetime)

### Introduction

The [`min()`](https://library.humio.com/data-analysis/functions-min.html) function can be used to find the smallest value in a numeric field across all matching events. It returns a single value representing the minimum found in a field named _min. 

In this example, the [`min()`](https://library.humio.com/data-analysis/functions-min.html) function is used to find the fastest response time from a set of web server logs. The response time is the time from the receipt of a request to the complete processing of the request. 

Example incoming data might look like this: 

@timestamp| endpoint| responsetime| status  
---|---|---|---  
2025-08-06T10:00:00Z| /api/users| 180| 200  
2025-08-06T10:00:01Z| /api/products| 2850| 200  
2025-08-06T10:00:02Z| /api/orders| 95| 200  
2025-08-06T10:00:03Z| /api/users| 450| 200  
2025-08-06T10:00:04Z| /api/products| 1275| 200  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         min(responsetime)

Calculates the minimum value found in the responsetime field across all events and returns the result in a new field named _min. 

If no events contain the specified field, or if the field contains non-numeric values, the function returns nothing. 

  3. Event Result set.




### Summary and Results

The query is used to find the fastest response time in the event set, helping identify the best-case performance scenario. Response time is an important parameter. The lower the response time, the better system performance. If server response time is high, it may indicate that the server is overloaded and having difficulties processing requests. 

This query is useful, for example, to establish performance baselines, identify optimal performance levels, or verify minimum service level agreements (SLAs). 

Sample output from the incoming example data: 

_min  
---  
95  
  
The result shows a response time of 95ms, which is considered excellent performance, well within the target range for optimal user experience. 

Note that the result shows the single smallest value found in the responsetime field across all events in the default output field _min. 

The minimum response time can be effectively displayed in a single value widget on a dashboard. For more comprehensive performance analysis, consider combining this with other aggregation functions like [`max()`](https://library.humio.com/data-analysis/functions-max.html) and [`avg()`](https://library.humio.com/data-analysis/functions-avg.html) to show the full range of response times. For an example, see [Calculate Minimum and Maximum Response Times](examples-min-max-response-squarebrackets.html "Calculate Minimum and Maximum Response Times").
