# time:second() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-time-second.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`time:second()`](functions-time-second.html "time:second\(\)")

Gets the second of a timestamp field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-time-second.html#query-functions-time-second-as)|  string| optional[a] | `_second`|  The name of the output field.   
[_`field`_](functions-time-second.html#query-functions-time-second-field)[b]| string| optional[[a]](functions-time-second.html#ftn.table-functions-time-second-optparamfn) | `@timestamp`|  The name of the input field.   
[_`timezone`_](functions-time-second.html#query-functions-time-second-timezone)|  string| optional[[a]](functions-time-second.html#ftn.table-functions-time-second-optparamfn) |  |  The time offset to use, for example, `-01:00`. If not specified, the query's offset will be used.   
[_`timezoneField`_](functions-time-second.html#query-functions-time-second-timezonefield)|  string| optional[[a]](functions-time-second.html#ftn.table-functions-time-second-optparamfn) | `@timezone`|  The name of the field containing the timezone to use, if not specified the query's timezone will be used. This is ignored if the timezone parameter is passed as well. If this is not defined the timezone offset of the query will be used.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-time-second.html#query-functions-time-second-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-time-second.html#query-functions-time-second-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     time:second("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     time:second(field="value")
> 
> These examples show basic structure only.

### [`time:second()`](functions-time-second.html "time:second\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Second From Timestamp

**Get the second from a timestamp using the[`time:second()`](functions-time-second.html "time:second\(\)") function **

##### Query

logscale
    
    
    time:second(timestamp, as=second)

##### Introduction

In this example, the [`time:second()`](functions-time-second.html "time:second\(\)") function is used to extract the seconds from a specific timestamp `2025-08-27 08:51:51.312`, demonstrating how to get the second value from a datetime. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         time:second(timestamp, as=second)

Extracts the seconds from the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named second. If the [_`as`_](functions-time-second.html#query-functions-time-second-as) parameter is not specified, the result is returned in a field named _second as default. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the seconds from a timestamp, which is useful for analyzing events at a second-level granularity. 

This query is useful, for example, to analyze per-second patterns, group events by second, or investigate timing patterns within minutes. 

Sample output from the incoming example data: 

@timestamp| second  
---|---  
2025-08-27 08:51:51.312| 51  
  
The result shows how the [`time:second()`](functions-time-second.html "time:second\(\)") function extracts the seconds (in this case `51`) from the timestamp, indicating it is 51 seconds into the minute. 

For visualizing this data, consider using a Bar Chart widget to show event distribution across seconds, or a Heat Map widget to display activity patterns within minutes. The [`time:second()`](functions-time-second.html "time:second\(\)") function is often used with other time functions like [`time:minute()`](functions-time-minute.html "time:minute\(\)") and [`time:millisecond()`](functions-time-millisecond.html "time:millisecond\(\)") for precise time analysis.
