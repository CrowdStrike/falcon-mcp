# time:millisecond() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-time-millisecond.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`time:millisecond()`](functions-time-millisecond.html "time:millisecond\(\)")

Gets the millisecond of a timestamp field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-time-millisecond.html#query-functions-time-millisecond-as)|  string| optional[a] | `_millisecond`|  The name of the output field.   
[_`field`_](functions-time-millisecond.html#query-functions-time-millisecond-field)[b]| string| optional[[a]](functions-time-millisecond.html#ftn.table-functions-time-millisecond-optparamfn) | `@timestamp`|  The name of the input field.   
[_`timezone`_](functions-time-millisecond.html#query-functions-time-millisecond-timezone)|  string| optional[[a]](functions-time-millisecond.html#ftn.table-functions-time-millisecond-optparamfn) |  |  The time offset to use, for example, `-01:00`. If not specified, the query's offset will be used.   
[_`timezoneField`_](functions-time-millisecond.html#query-functions-time-millisecond-timezonefield)|  string| optional[[a]](functions-time-millisecond.html#ftn.table-functions-time-millisecond-optparamfn) | `@timezone`|  The name of the field containing the timezone to use, if not specified the query's timezone will be used. This is ignored if the timezone parameter is passed as well. If this is not defined the timezone offset of the query will be used.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-time-millisecond.html#query-functions-time-millisecond-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-time-millisecond.html#query-functions-time-millisecond-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     time:millisecond("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     time:millisecond(field="value")
> 
> These examples show basic structure only.

### [`time:millisecond()`](functions-time-millisecond.html "time:millisecond\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Millisecond From Timestamp

**Get the millisecond from a timestamp using the[`time:millisecond()`](functions-time-millisecond.html "time:millisecond\(\)") function **

##### Query

logscale
    
    
    time:millisecond(timestamp, as=ms)

##### Introduction

In this example, the [`time:millisecond()`](functions-time-millisecond.html "time:millisecond\(\)") function is used to extract the milliseconds from a specific timestamp `2025-08-27 08:51:51.312`, demonstrating how to get the millisecond value from a datetime. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         time:millisecond(timestamp, as=ms)

Extracts the milliseconds from the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named ms. If the [_`as`_](functions-time-millisecond.html#query-functions-time-millisecond-as) parameter is not specified, the result is returned in a field named _millisecond as default. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the milliseconds from a timestamp, which is useful for analyzing events at a sub-second level of precision. 

This query is useful, for example, to analyze high-precision timing, measure small time differences, or investigate event sequencing at millisecond resolution. 

Sample output from the incoming example data: 

@timestamp| ms  
---|---  
2025-08-27 08:51:51.312| 312  
  
The result shows how the [`time:millisecond()`](functions-time-millisecond.html "time:millisecond\(\)") function extracts the milliseconds (in this case `312`) from the timestamp, indicating there are 312 milliseconds in this timestamp. 

For visualizing this data, consider using a Scatter Plot widget to show event distribution within seconds, or a Line Chart widget to display high-precision timing patterns. The [`time:millisecond()`](functions-time-millisecond.html "time:millisecond\(\)") function is often used with other time functions like [`time:second()`](functions-time-second.html "time:second\(\)") and [`time:minute()`](functions-time-minute.html "time:minute\(\)") for precise time analysis.
