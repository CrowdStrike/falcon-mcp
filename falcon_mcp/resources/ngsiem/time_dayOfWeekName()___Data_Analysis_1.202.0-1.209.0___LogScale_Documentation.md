# time:dayOfWeekName() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-time-dayofweekname.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`time:dayOfWeekName()`](functions-time-dayofweekname.html "time:dayOfWeekName\(\)")

Gets the English display name of day of the week of a timestamp field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-time-dayofweekname.html#query-functions-time-dayofweekname-as)|  string| optional[a] | `_dayOfWeekName`|  The name of the output field.   
[_`field`_](functions-time-dayofweekname.html#query-functions-time-dayofweekname-field)[b]| string| optional[[a]](functions-time-dayofweekname.html#ftn.table-functions-time-dayofweekname-optparamfn) | `@timestamp`|  The name of the input field.   
[_`timezone`_](functions-time-dayofweekname.html#query-functions-time-dayofweekname-timezone)|  string| optional[[a]](functions-time-dayofweekname.html#ftn.table-functions-time-dayofweekname-optparamfn) |  |  The time offset to use, for example, `-01:00`. If not specified, the query's offset will be used.   
[_`timezoneField`_](functions-time-dayofweekname.html#query-functions-time-dayofweekname-timezonefield)|  string| optional[[a]](functions-time-dayofweekname.html#ftn.table-functions-time-dayofweekname-optparamfn) | `@timezone`|  The name of the field containing the timezone to use, if not specified the query's timezone will be used. This is ignored if the timezone parameter is passed as well. If this is not defined the timezone offset of the query will be used.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-time-dayofweekname.html#query-functions-time-dayofweekname-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-time-dayofweekname.html#query-functions-time-dayofweekname-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     time:dayOfWeekName("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     time:dayOfWeekName(field="value")
> 
> These examples show basic structure only.

### [`time:dayOfWeekName()`](functions-time-dayofweekname.html "time:dayOfWeekName\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Day of Week Name From Timestamp

**Get the name of the weekday from a timestamp using the[`time:dayOfWeekName()`](functions-time-dayofweekname.html "time:dayOfWeekName\(\)") function **

##### Query

logscale
    
    
    time:dayOfWeekName(timestamp, as=weekday)

##### Introduction

In this example, the [`time:dayOfWeekName()`](functions-time-dayofweekname.html "time:dayOfWeekName\(\)") function is used to extract the weekday name from a specific timestamp `2025-08-27 08:51:51.000`, demonstrating how to get the day name from a datetime. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         time:dayOfWeekName(timestamp, as=weekday)

Extracts the name of the weekday from the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named weekday. If the [_`as`_](functions-time-dayofweekname.html#query-functions-time-dayofweekname-as) parameter is not specified, the result is returned in a field named _dayOfWeekName as default. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the weekday name from a timestamp, which is useful for creating human-readable output and reports. 

This query is useful, for example, to generate readable reports, create user-friendly displays, or label data with weekday names. 

Sample output from the incoming example data: 

@timestamp| weekday  
---|---  
2025-08-27 08:51:51.000| Wednesday  
  
The result shows how the [`time:dayOfWeekName()`](functions-time-dayofweekname.html "time:dayOfWeekName\(\)") function extracts the day name (in this case `Wednesday`) from the timestamp, returning it as a string value. 

For visualizing this data, consider using a Bar Chart widget to show event counts by day name, or a Table widget to display events with their corresponding weekday names. The [`time:dayOfWeekName()`](functions-time-dayofweekname.html "time:dayOfWeekName\(\)") function is often used with other time functions like [`time:month()`](functions-time-month.html "time:month\(\)") and [`time:year()`](functions-time-year.html "time:year\(\)") for complete date analysis.
