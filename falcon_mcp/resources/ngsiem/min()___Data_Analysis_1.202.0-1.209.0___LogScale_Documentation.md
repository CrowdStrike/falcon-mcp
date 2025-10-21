# min() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-min.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`min()`](functions-min.html "min\(\)")

Finds the smallest number for the specified field over a set of events. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-min.html#query-functions-min-as)|  string| optional[a] | `_min`|  Name of output field.   
[_`field`_](functions-min.html#query-functions-min-field)[b]| string| required |  |  Field to extract a number from.   
[_`type`_](functions-min.html#query-functions-min-type)|  string| optional[[a]](functions-min.html#ftn.table-functions-min-optparamfn) |  |  description   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-min.html#query-functions-min-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-min.html#query-functions-min-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     min("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     min(field="value")
> 
> These examples show basic structure only.

### [`min()`](functions-min.html "min\(\)") Syntax Examples

Return what was the minimum responsetime: 

logscale
    
    
    min(responsetime)

Filter for events with a responsetime greater than 5 seconds: 

logscale
    
    
    min(responsetime)
    | _min> 5

### [`min()`](functions-min.html "min\(\)") Examples

Click + next to an example below to get the full details.

#### Alert Query for Parsers Issues

**Reporting errors**

##### Query

logscale
    
    
    #type=humio #kind=logs
    | loglevel=WARN
    | class = c.h.d.ParserLimitingJob
    | "Setting reject ingest for"
    | groupBy(id, function=[count(), min(@timestamp), max(@timestamp)] )
    | timeDiff:=_max-_min
    | timeDiff > 300000 and _count > 10

##### Introduction

This alert query tries to balance reacting when there are problems with parsers, without being too restrictive. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #type=humio #kind=logs

Filters on all logs across all hosts in the cluster. 

  3. logscale
         
         | loglevel=WARN

Filters for all events where the loglevel is equal to `WARN`. 

  4. logscale
         
         | class = c.h.d.ParserLimitingJob

Assigns the value `c.h.d.ParserLimitingJob` to the class for the logs having the loglevel value `WARN`. 

  5. logscale
         
         | "Setting reject ingest for"

Filters for events containing the string `Setting reject ingest for`. This is the error message generated when ingested events are rejected. 

  6. logscale
         
         | groupBy(id, function=[count(), min(@timestamp), max(@timestamp)] )

Groups the returned result by the field id, makes a count on the events and returns the minimum timestamp and maximum timestamp. This returns a new event set, with the fields id, _count, _min, and _max. 

  7. logscale
         
         | timeDiff:=_max-_min

Calculates the time difference between the maximum timestamp values and the minimum timestamp values and returns the result in a new field named timeDiff. 

  8. logscale
         
         | timeDiff > 300000 and _count > 10

Returns all events where the values of timeDiff is greater that `300000` and where there are more than `10` occurrences. 

  9. Event Result set.




##### Summary and Results

This query is used to set up alerts for parsers issues. Setting up alerts for parsers issues will allow to proactively reach out to customers where their queries are being throttled and help them. 

#### Calculate Minimum and Maximum Response Times

**Calculate minimum and maximum response times using multiple aggregate functions in square brackets**

##### Query

logscale
    
    
    [min_response := min(responsetime), max_response := max(responsetime)]

##### Introduction

In this example, the [`min()`](functions-min.html "min\(\)") and [`max()`](functions-max.html "max\(\)") functions are used to find the shortest and longest response times, with results stored in named fields. 

Square brackets allow multiple aggregations to be performed in a single operation 

Writing a list of aggregators in square brackets is a shorthand syntax for the [`stats()`](functions-stats.html "stats\(\)") function. 

Example incoming data might look like this: 

@timestamp| endpoint| responsetime| status_code  
---|---|---|---  
1686837825000| /api/users| 145| 200  
1686837826000| /api/products| 892| 200  
1686837827000| /api/orders| 167| 200  
1686837828000| /api/payment| 1290| 500  
1686837829000| /api/users| 156| 200  
1686837830000| /api/items| 78| 200  
1686837831000| /api/orders| 934| 200  
1686837832000| /api/checkout| 923| 200  
1686837833000| /api/products| 134| 200  
1686837834000| /api/users| 445| 200  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         [min_response := min(responsetime), max_response := max(responsetime)]

In a single operation, calculates the minimum value from the responsetime field and returns the results in a field named min_response, and calculates the maximum value from the responsetime field and returns the results in a field named max_response. 

Square brackets allow multiple aggregations to be performed in a single operation 

  3. Event Result set.




##### Summary and Results

The query is used to find the range of response times by calculating both the minimum and maximum values. 

The results are returned in fields with names specified in the field assignments 

This query is useful, for example, to monitor service performance, identify outliers in response times, or establish performance baselines. 

Sample output from the incoming example data: 

min_response| max_response  
---|---  
78| 1290  
  
Note that only one row is returned containing both calculated values. 

#### Find Minimum Value in Field

**Calculate the minimum value in a numeric field using the[`min()`](functions-min.html "min\(\)") function **

##### Query

logscale
    
    
    min(responsetime)

##### Introduction

In this example, the [`min()`](functions-min.html "min\(\)") function is used to find the fastest response time from a set of web server logs. The response time is the time from the receipt of a request to the complete processing of the request. 

Example incoming data might look like this: 

@timestamp| endpoint| responsetime| status  
---|---|---|---  
2025-08-06T10:00:00Z| /api/users| 180| 200  
2025-08-06T10:00:01Z| /api/products| 2850| 200  
2025-08-06T10:00:02Z| /api/orders| 95| 200  
2025-08-06T10:00:03Z| /api/users| 450| 200  
2025-08-06T10:00:04Z| /api/products| 1275| 200  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         min(responsetime)

Calculates the minimum value found in the responsetime field across all events and returns the result in a new field named _min. 

If no events contain the specified field, or if the field contains non-numeric values, the function returns nothing. 

  3. Event Result set.




##### Summary and Results

The query is used to find the fastest response time in the event set, helping identify the best-case performance scenario. Response time is an important parameter. The lower the response time, the better system performance. If server response time is high, it may indicate that the server is overloaded and having difficulties processing requests. 

This query is useful, for example, to establish performance baselines, identify optimal performance levels, or verify minimum service level agreements (SLAs). 

Sample output from the incoming example data: 

_min  
---  
95  
  
The result shows a response time of 95ms, which is considered excellent performance, well within the target range for optimal user experience. 

Note that the result shows the single smallest value found in the responsetime field across all events in the default output field _min. 

The minimum response time can be effectively displayed in a single value widget on a dashboard. For more comprehensive performance analysis, consider combining this with other aggregation functions like [`max()`](functions-max.html "max\(\)") and [`avg()`](functions-avg.html "avg\(\)") to show the full range of response times. For an example, see [Calculate Minimum and Maximum Response Times](https://library.humio.com/examples/examples-min-max-response-squarebrackets.html).
