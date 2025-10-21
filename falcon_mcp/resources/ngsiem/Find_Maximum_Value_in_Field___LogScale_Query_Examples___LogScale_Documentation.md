# Find Maximum Value in Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-max-response-time-slow.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Maximum Value in Field

Calculate the maximum value in a numeric field using the [`max()`](https://library.humio.com/data-analysis/functions-max.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    max(responsetime)

### Introduction

The [`max()`](https://library.humio.com/data-analysis/functions-max.html) function can be used to find the largest value in a numeric field across all matching events. It returns a single value representing the maximum found in a field named _max. 

In this example, the [`max()`](https://library.humio.com/data-analysis/functions-max.html) function is used to find the slowest response time from a set of web server logs. The response time is the time from the receipt of a request to the complete processing of the request. 

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
         
         max(responsetime)

Calculates the maximum value found in the responsetime field across all events and returns the result in a new field named _max. If server response time is high, it may indicate that the server is overloaded and having difficulties processing requests. 

If no events contain the specified field, or if the field contains non-numeric values, the function returns nothing. 

  3. Event Result set.




### Summary and Results

The query is used to find the slowest response time in the event set, helping identify potential performance issues. Response time is an important parameter. If server response time is high, it may indicate that the server is overloaded and having difficulties processing requests. 

This query is useful, for example, to identify performance bottlenecks, monitor service level agreement (SLA) breaches, or detect abnormal response times. 

Sample output from the incoming example data: 

_max  
---  
2850  
  
The result shows a response time of 2850ms (2.85 seconds), which falls into the poor performance category and could indicate a significant performance issue requiring investigation. 

Note that the result shows the single largest value found in the responsetime field across all events in the default output field _max. 

The maximum response time can be effectively displayed in a single value widget on a dashboard. For more comprehensive performance analysis, consider combining this with other aggregation functions like [`min()`](https://library.humio.com/data-analysis/functions-min.html) and [`avg()`](https://library.humio.com/data-analysis/functions-avg.html) to show the full range of response times. For an example, see [Calculate Minimum and Maximum Response Times](examples-min-max-response-squarebrackets.html "Calculate Minimum and Maximum Response Times").
