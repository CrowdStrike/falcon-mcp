# time:minute() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-time-minute.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`time:minute()`](functions-time-minute.html "time:minute\(\)")

Gets the minute of a timestamp field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-time-minute.html#query-functions-time-minute-as)|  string| optional[a] | `_minute`|  The name of the output field.   
[_`field`_](functions-time-minute.html#query-functions-time-minute-field)[b]| string| optional[[a]](functions-time-minute.html#ftn.table-functions-time-minute-optparamfn) | `@timestamp`|  The name of the input field.   
[_`timezone`_](functions-time-minute.html#query-functions-time-minute-timezone)|  string| optional[[a]](functions-time-minute.html#ftn.table-functions-time-minute-optparamfn) |  |  The time offset to use, for example, `-01:00`. If not specified, the query's offset will be used.   
[_`timezoneField`_](functions-time-minute.html#query-functions-time-minute-timezonefield)|  string| optional[[a]](functions-time-minute.html#ftn.table-functions-time-minute-optparamfn) | `@timezone`|  The name of the field containing the timezone to use, if not specified the query's timezone will be used. This is ignored if the timezone parameter is passed as well. If this is not defined the timezone offset of the query will be used.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-time-minute.html#query-functions-time-minute-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-time-minute.html#query-functions-time-minute-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     time:minute("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     time:minute(field="value")
> 
> These examples show basic structure only.

### [`time:minute()`](functions-time-minute.html "time:minute\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Minute From Timestamp

**Get the minute from a timestamp using the[`time:minute()`](functions-time-minute.html "time:minute\(\)") function **

##### Query

logscale
    
    
    time:minute(timestamp, as=minute)

##### Introduction

In this example, the [`time:minute()`](functions-time-minute.html "time:minute\(\)") function is used to extract the minute from a specific timestamp `2025-08-27 08:51:51.312`, demonstrating how to get the minute value from a datetime. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         time:minute(timestamp, as=minute)

Extracts the minute from the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named minute. If the [_`as`_](functions-time-minute.html#query-functions-time-minute-as) parameter is not specified, the result is returned in a field named _minute as default. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the minute from a timestamp, which is useful for analyzing events at a minute-level granularity. 

This query is useful, for example, to analyze per-minute patterns, group events by minute, or investigate timing patterns within hours. 

Sample output from the incoming example data: 

@timestamp| minute  
---|---  
2025-08-27 08:51:51.312| 51  
  
The result shows how the [`time:minute()`](functions-time-minute.html "time:minute\(\)") function extracts the minute (in this case `51`) from the timestamp, indicating it is 51 minutes past the hour. 

For visualizing this data, consider using a Bar Chart widget to show event distribution across minutes, or a Heat Map widget to display activity patterns within hours. The [`time:minute()`](functions-time-minute.html "time:minute\(\)") function is often used with other time functions like [`time:hour()`](functions-time-hour.html "time:hour\(\)") and [`time:second()`](functions-time-second.html "time:second\(\)") for detailed time analysis.
