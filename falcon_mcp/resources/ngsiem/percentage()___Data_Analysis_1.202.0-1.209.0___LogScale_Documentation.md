# percentage() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-percentage.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Page was created:Aug 5, 2025

## [`percentage()`](functions-percentage.html "percentage\(\)")

The [`percentage()`](functions-percentage.html "percentage\(\)") function calculates the proportion of events that match specified conditions. The function returns a floating-point number between 0 and 100. 

Use the [`format()`](functions-format.html "format\(\)") function to control decimal precision in the output. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-percentage.html#query-functions-percentage-as)|  string| optional[a] | `_percentage`|  Name of the output field containing the calculated percentage.   
[_`condition`_](functions-percentage.html#query-functions-percentage-condition)[b]| non-aggregate pipeline| required |  |  A non-aggregate pipeline that defines matching criteria for events. If an event passes through the pipeline, the event is included, otherwise it is excluded.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`condition`_](functions-percentage.html#query-functions-percentage-condition) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`condition`_](functions-percentage.html#query-functions-percentage-condition) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     percentage("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     percentage(condition="value")
> 
> These examples show basic structure only.

### [`percentage()`](functions-percentage.html "percentage\(\)") Syntax Examples

This example shows how to find the percentage of successful requests: [ percentage({status=2*}) _percentage -> 50 ] 

If the input data was "status=200","status=201","status=400","status=500", the result would be: 

logscale
    
    
    "_percentage"
    "50"

This example shows how to calculate error rates from HTTP status codes (client and server error percentage): 

logscale
    
    
    [
        percentage({status=4*}, as=clientErrorPct),
        percentage({status=5*}, as=serverErrorPct)
    ]

If the input data was "status=200","status=201","status=200","status=301","status=400","status=500", the result would be: 

logscale
    
    
    "clientErrorPct","serverErrorPct" 
    "16.666666666666664","16.666666666666664"

### [`percentage()`](functions-percentage.html "percentage\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate HTTP Error Percentages

**Compute the percentage of client and server errors in HTTP traffic using the[`percentage()`](functions-percentage.html "percentage\(\)") function **

##### Query

logscale
    
    
    [
            percentage({status=4*}, as=clientErrorPct),
            percentage({status=5*}, as=serverErrorPct)
    ]

##### Introduction

In this example, the [`percentage()`](functions-percentage.html "percentage\(\)") function is used to calculate both client-side (`4xx`) and server-side (`5xx`) error rates from HTTP status codes simultaneously using an array (multiple [`percentage()`](functions-percentage.html "percentage\(\)") calculations). 

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
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         [
                 percentage({status=4*}, as=clientErrorPct),
                 percentage({status=5*}, as=serverErrorPct)
         ]

Creates an array of two [`percentage()`](functions-percentage.html "percentage\(\)") calculations: 

     * The first [`percentage()`](functions-percentage.html "percentage\(\)") calculates the percentage of events where [status](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-aggregatealert-alert.html) starts with `4` (client errors) and returns the result in a new field named clientErrorPct

     * The second [`percentage()`](functions-percentage.html "percentage\(\)") calculates the percentage of events where [status](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-aggregatealert-alert.html) starts with `5` (server errors) and returns the result in a new field named serverErrorPct

The wildcard `*` is used to match any digits after 4 or 5 in the status code. 

  3. Event Result set.




##### Summary and Results

The query is used to calculate two different error rates simultaneously from HTTP status codes, providing insights into both client-side and server-side errors as percentages of total requests. 

Note how the query uses multiple [`percentage()`](functions-percentage.html "percentage\(\)") calculations within an array to simultaneously compute the percentage of `4xx` (client) and `5xx` (server) errors in HTTP traffic. 

This query is useful, for example, to monitor the health of a web application by tracking error rates, setting up alerts when error percentages exceed certain thresholds, or creating dashboards showing error trends over time. 

Sample output from the incoming example data: 

clientErrorPct| serverErrorPct  
---|---  
30| 30  
  
The percentages are calculated as decimal numbers between 0 and 100. In this example, 3 out of 10 events are `4xx` errors (30%) and 3 out of 10 are `5xx` errors (30%). 

The results can be used directly in visualizations or for further calculations. Use the [`format()`](functions-format.html "format\(\)") function to control decimal precision in the output.
