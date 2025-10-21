# Calculate HTTP Error Percentages | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-percentage-http-errors.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate HTTP Error Percentages

Compute the percentage of client and server errors in HTTP traffic using the [`percentage()`](https://library.humio.com/data-analysis/functions-percentage.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    [
            percentage({status=4*}, as=clientErrorPct),
            percentage({status=5*}, as=serverErrorPct)
    ]

### Introduction

The [`percentage()`](https://library.humio.com/data-analysis/functions-percentage.html) function can be used to calculate what percentage of events match specific criteria compared to the total number of events in the result set. 

In this example, the [`percentage()`](https://library.humio.com/data-analysis/functions-percentage.html) function is used to calculate both client-side (`4xx`) and server-side (`5xx`) error rates from HTTP status codes simultaneously using an array (multiple [`percentage()`](https://library.humio.com/data-analysis/functions-percentage.html) calculations). 

@timestamp| status| path| response_time  
---|---|---|---  
2023-06-15T10:00:00Z| 200| /api/users| 0.123  
2023-06-15T10:00:01Z| 404| /api/missing| 0.045  
2023-06-15T10:00:02Z| 500| /api/error| 2.345  
2023-06-15T10:00:03Z| 200| /api/products| 0.167  
2023-06-15T10:00:04Z| 403| /api/restricted| 0.078  
2023-06-15T10:00:05Z| 502| /api/gateway| 1.234  
2023-06-15T10:00:06Z| 200| /api/orders| 0.189  
2023-06-15T10:00:07Z| 429| /api/ratelimit| 0.056  
2023-06-15T10:00:08Z| 503| /api/unavailable| 3.456  
2023-06-15T10:00:09Z| 200| /api/cart| 0.145  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         [
                 percentage({status=4*}, as=clientErrorPct),
                 percentage({status=5*}, as=serverErrorPct)
         ]

Creates an array of two [`percentage()`](https://library.humio.com/data-analysis/functions-percentage.html) calculations: 

     * The first [`percentage()`](https://library.humio.com/data-analysis/functions-percentage.html) calculates the percentage of events where [status](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-aggregatealert-alert.html) starts with `4` (client errors) and returns the result in a new field named clientErrorPct

     * The second [`percentage()`](https://library.humio.com/data-analysis/functions-percentage.html) calculates the percentage of events where [status](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-aggregatealert-alert.html) starts with `5` (server errors) and returns the result in a new field named serverErrorPct

The wildcard `*` is used to match any digits after 4 or 5 in the status code. 

  3. Event Result set.




### Summary and Results

The query is used to calculate two different error rates simultaneously from HTTP status codes, providing insights into both client-side and server-side errors as percentages of total requests. 

Note how the query uses multiple [`percentage()`](https://library.humio.com/data-analysis/functions-percentage.html) calculations within an array to simultaneously compute the percentage of `4xx` (client) and `5xx` (server) errors in HTTP traffic. 

This query is useful, for example, to monitor the health of a web application by tracking error rates, setting up alerts when error percentages exceed certain thresholds, or creating dashboards showing error trends over time. 

Sample output from the incoming example data: 

clientErrorPct| serverErrorPct  
---|---  
30| 30  
  
The percentages are calculated as decimal numbers between 0 and 100. In this example, 3 out of 10 events are `4xx` errors (30%) and 3 out of 10 are `5xx` errors (30%). 

The results can be used directly in visualizations or for further calculations. Use the [`format()`](https://library.humio.com/data-analysis/functions-format.html) function to control decimal precision in the output.
