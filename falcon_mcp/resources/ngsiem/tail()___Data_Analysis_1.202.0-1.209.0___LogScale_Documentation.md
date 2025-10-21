# tail() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-tail.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`tail()`](functions-tail.html "tail\(\)")

Retrieves the most recent events and returns a specified maximum number of events. The [`tail()`](functions-tail.html "tail\(\)") function sorts events by either [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) or [@ingesttimestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-ingesttimestamp), depending on their availability. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`limit`_](functions-tail.html#query-functions-tail-limit)[a]| number| optional[b] | `200`|  The argument given to this parameter determines the limit on the number of events included in the result of the function. The default argument is `default`. The maximum is controlled by the [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html) dynamic configuration, which is [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html) by default. If the argument is `max` (`limit=max`), then the value of [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html) is used.   
|  |  | **Values**  
|  |  | [`max`](functions-tail.html#query-functions-tail-limit-option-max)| An alias to use the maximum limit set by [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html)  
|  | **Minimum**| `1`|   
|  | **Maximum**| `200,000`|   
|  | **Controlling Variables**  
|  | [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html)|  **Variable default:**`200,000 rows`  
[a] The parameter name [_`limit`_](functions-tail.html#query-functions-tail-limit) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`limit`_](functions-tail.html#query-functions-tail-limit) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     tail("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     tail(limit="value")
> 
> These examples show basic structure only.

### [`tail()`](functions-tail.html "tail\(\)") Function Operation

As default, the [`tail()`](functions-tail.html "tail\(\)") function uses the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field to select the most recent events. If not available, the [@ingesttimestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-ingesttimestamp) field is used instead. 

If neither the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) or [@ingesttimestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-ingesttimestamp) fields are available, the search will report the error: [Expected events to have a @timestamp field for tail to work](functions-tail.html "tail\(\)"). 

The maximum value of the [_`limit`_](functions-tail.html#query-functions-tail-limit) parameter can be adjusted using the [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html) dynamic configuration. 

### [`tail()`](functions-tail.html "tail\(\)") Syntax Examples

Select the 10 newest where `loglevel=ERROR`: 

logscale
    
    
    loglevel=ERROR
    | tail(10)

Select the 100 latest events and group them by loglevel

logscale
    
    
    tail(limit=100)
    | groupBy(loglevel)

Although the default is 200, if a number higher than this is specified, LogScale will attempt to return as many results up to that number. For example: 

logscale
    
    
    "GET /_images"
    | tail(1000)

Will return up to 1000 events matching an HTTP GET request for files in the `_images` directory. If there are only 287 matching events, all 287 will be returned. 

### [`tail()`](functions-tail.html "tail\(\)") Examples

Click + next to an example below to get the full details.

#### Deduplicate Content by Field

**Deduplicating content based on a specific field**

##### Query

logscale
    
    
    groupBy(field, function=tail(1))

##### Introduction

If you want to deduplicate events by a given field, for example to identify a unique list of events for further processing, you can use an aggregate function. In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") function is used with [`tail()`](functions-tail.html "tail\(\)") to use the last value in a sequence of events. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(field, function=tail(1))

Groups all events in a specific field, and reduces the results using [`tail()`](functions-tail.html "tail\(\)") to take only the last value. 

  3. Event Result set.




##### Summary and Results

The query is used to deduplicate events by a given field. This is useful if you want to create a unique list of events for further processing.
