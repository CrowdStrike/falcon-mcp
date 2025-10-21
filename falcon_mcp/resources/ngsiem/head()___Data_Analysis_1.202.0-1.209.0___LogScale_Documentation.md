# head() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-head.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`head()`](functions-head.html "head\(\)")

Retrieves the oldest events first and returns a specified maximum number of events. The [`head()`](functions-head.html "head\(\)") function sorts events by either [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) or [@ingesttimestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-ingesttimestamp), depending on the selected query parameters. This function is equivalent to the command-line **head** tool. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`limit`_](functions-head.html#query-functions-head-limit)[a]| number| optional[b] | `200`|  The argument given to this parameter determines the limit on the number of events included in the result of the function. The default argument is `default`. The maximum is controlled by the [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html) dynamic configuration, which is [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html) by default. If the argument is `max` (`limit=max`), then the value of [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html) is used.   
|  |  | **Values**  
|  |  | [`max`](functions-head.html#query-functions-head-limit-option-max)| An alias to use the maximum limit set by [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html)  
|  | **Minimum**| `0`|   
|  | **Maximum**| `200,000`|   
|  | **Controlling Variables**  
|  | [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html)|  **Variable default:**`200,000 rows`  
[a] The parameter name [_`limit`_](functions-head.html#query-functions-head-limit) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`limit`_](functions-head.html#query-functions-head-limit) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     head("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     head(limit="value")
> 
> These examples show basic structure only.

The maximum value of the _`limit`_ parameter can be adjusted using the [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html) dynamic configuration. 

### Note

The [`head()`](functions-head.html "head\(\)") function is often used with [Sequence Query Functions](functions-sequence.html "Sequence Query Functions"), as these functions must be used after an aggregator function to ensure event ordering. 

### [`head()`](functions-head.html "head\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Running Average of Field Values

**Calculate a running average of values in a dataset using the[`accumulate()`](functions-accumulate.html "accumulate\(\)") function **

##### Query

logscale
    
    
    head()
    | accumulate(avg(value))

##### Introduction

In this example, the [`accumulate()`](functions-accumulate.html "accumulate\(\)") function is used with the [`avg()`](functions-avg.html "avg\(\)") function to calculate a running average of the field value. 

Note that the [`accumulate()`](functions-accumulate.html "accumulate\(\)") function must be used after an aggregator function, in this example the [`head()`](functions-head.html "head\(\)") function, to ensure event ordering. 

Example incoming data might look like this: 

key| value  
---|---  
a| 5  
b| 6  
c| 1  
d| 2  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         head()

Ensures that the events are ordered by time, selecting the oldest events. 

  3. logscale
         
         | accumulate(avg(value))

Computes the running average of all values, including the current one, using the [`accumulate()`](functions-accumulate.html "accumulate\(\)") function with the [`avg()`](functions-avg.html "avg\(\)") aggregator. 

  4. Event Result set.




##### Summary and Results

The query is used to calculate the running average of fields. The query calculates moving averages that change as new values arrive. 

Sample output from the incoming example data: 

_avg| key| value  
---|---|---  
5| a| 5  
5.5| b| 6  
4| c| 1  
3.5| d| 2  
  
#### Get First Events From Result Set

**Limit the number of events returned using the[`head()`](functions-head.html "head\(\)") function **

##### Query

logscale
    
    
    loglevel=ERROR
    head(10)

##### Introduction

In this example, the [`head()`](functions-head.html "head\(\)") function is used to return the first 10 error events from the event set. 

Example incoming data might look like this: 

@timestamp| loglevel| service| message  
---|---|---|---  
2025-08-06T10:00:00Z| ERROR| authentication| Failed login attempt for user 'admin'  
2025-08-06T10:00:05Z| INFO| authentication| Successful login for user 'john'  
2025-08-06T10:00:10Z| ERROR| database| Connection timeout to primary database  
2025-08-06T10:00:15Z| WARN| api| Rate limit threshold reached  
2025-08-06T10:00:20Z| ERROR| authentication| Invalid credentials provided  
2025-08-06T10:00:25Z| INFO| api| Request processed successfully  
2025-08-06T10:00:30Z| ERROR| database| Query execution failed  
2025-08-06T10:00:35Z| ERROR| api| Internal server error  
2025-08-06T10:00:40Z| INFO| authentication| User logout  
2025-08-06T10:00:45Z| ERROR| database| Index corruption detected  
2025-08-06T10:00:50Z| ERROR| api| Service unavailable  
2025-08-06T10:00:55Z| ERROR| authentication| Account locked due to multiple failures  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         loglevel=ERROR

Filters events where the loglevel field equals `ERROR`. 

  3. logscale
         
         head(10)

Returns the first 10 events from the filtered result set. If no [_`limit`_](functions-head.html#query-functions-head-limit) parameter is specified, the [`head()`](functions-head.html "head\(\)") function defaults to returning 200 events. The events are returned in the order they were received, starting from the oldest event in the time range. 

`head(10)` is equal to `head(limit=10)`. 

  4. Event Result set.




##### Summary and Results

The query is used to find the first 10 error events in the event set, helping to identify the earliest error occurrences within the specified time range. 

This query is useful, for example, to quickly investigate the beginning of an incident or to get a sample of error events for troubleshooting. 

Sample output from the incoming example data: 

@timestamp| loglevel| service| message  
---|---|---|---  
2025-08-06T10:00:00Z| ERROR| authentication| Failed login attempt for user 'admin'  
2025-08-06T10:00:10Z| ERROR| database| Connection timeout to primary database  
2025-08-06T10:00:20Z| ERROR| authentication| Invalid credentials provided  
2025-08-06T10:00:30Z| ERROR| database| Query execution failed  
2025-08-06T10:00:35Z| ERROR| api| Internal server error  
2025-08-06T10:00:45Z| ERROR| database| Index corruption detected  
2025-08-06T10:00:50Z| ERROR| api| Service unavailable  
2025-08-06T10:00:55Z| ERROR| authentication| Account locked due to multiple failures  
  
Note that only events with loglevel=`ERROR` are included in the output, and the results are ordered chronologically. 

#### Group First Events by Log Level

**Limit and group events using[`head()`](functions-head.html "head\(\)") and [`groupBy()`](functions-groupby.html "groupBy\(\)") functions **

##### Query

logscale
    
    
    head(limit=10)
    groupBy(loglevel)

##### Introduction

In this example, the [`head()`](functions-head.html "head\(\)") function is used to limit the result set to 100 events, which are then grouped by their log level using the [`groupBy()`](functions-groupby.html "groupBy\(\)") function. 

Example incoming data might look like this: 

@timestamp| loglevel| service| message| status_code  
---|---|---|---|---  
2025-09-01T10:00:00Z| ERROR| authentication| Failed login attempt| 401  
2025-09-01T10:00:05Z| INFO| authentication| Successful login| 200  
2025-09-01T10:00:10Z| ERROR| database| Connection timeout| 503  
2025-09-01T10:00:15Z| WARN| api| Rate limit approaching| 429  
2025-09-01T10:00:20Z| ERROR| authentication| Invalid token| 401  
2025-09-01T10:00:25Z| INFO| api| Request processed| 200  
2025-09-01T10:00:30Z| DEBUG| database| Query executed| 200  
2025-09-01T10:00:35Z| ERROR| api| Internal error| 500  
2025-09-01T10:00:40Z| INFO| authentication| User logout| 200  
2025-09-01T10:00:45Z| WARN| database| High CPU usage| 200  
2025-09-01T10:00:50Z| DEBUG| api| Cache hit| 200  
2025-09-01T10:00:55Z| ERROR| authentication| Session expired| 401  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         head(limit=10)

Returns the first 10 events from the dataset. The [_`limit`_](functions-head.html#query-functions-head-limit) parameter explicitly specifies the number of events to return. The events are returned in the order they were received, starting from the oldest event in the time range. 

  3. logscale
         
         groupBy(loglevel)

Groups the events by the values in the loglevel field. The [`groupBy()`](functions-groupby.html "groupBy\(\)") function creates buckets for each unique value and counts the number of events in each bucket. By default, it creates a field named _count containing the number of events in each group. 

  4. Event Result set.




##### Summary and Results

The query is used to analyze the distribution of log levels across the first 10 events in the dataset. If `head(limit=100)` it would have returned 100 events. 

This query is useful, for example, to quickly assess the proportion of different log levels in a sample of events or to identify if there is an unusual distribution of log severities. 

Sample output from the incoming example data: 

loglevel| _count  
---|---  
ERROR| 5  
INFO| 3  
WARN| 2  
DEBUG| 2  
  
Note that the output shows the count of events for each log level found within the first 10 events, providing a quick overview of the log level distribution in the sample.
