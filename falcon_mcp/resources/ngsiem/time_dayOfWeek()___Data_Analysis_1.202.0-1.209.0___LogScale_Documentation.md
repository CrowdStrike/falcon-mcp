# time:dayOfWeek() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-time-dayofweek.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`time:dayOfWeek()`](functions-time-dayofweek.html "time:dayOfWeek\(\)")

Gets the day of the week from 1 (Monday) to 7 (Sunday) of a timestamp field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-time-dayofweek.html#query-functions-time-dayofweek-as)|  string| optional[a] | `_dayOfWeek`|  The name of the output field.   
[_`field`_](functions-time-dayofweek.html#query-functions-time-dayofweek-field)[b]| string| required | `@timestamp`|  The name of the input field.   
[_`timezone`_](functions-time-dayofweek.html#query-functions-time-dayofweek-timezone)|  string| optional[[a]](functions-time-dayofweek.html#ftn.table-functions-time-dayofweek-optparamfn) |  |  The time offset to use, for example, `-01:00`. If not specified, the query's offset will be used.   
[_`timezoneField`_](functions-time-dayofweek.html#query-functions-time-dayofweek-timezonefield)|  string| optional[[a]](functions-time-dayofweek.html#ftn.table-functions-time-dayofweek-optparamfn) | `@timezone`|  The name of the field containing the timezone to use, if not specified the query's timezone will be used. This is ignored if the timezone parameter is passed as well. If this is not defined the timezone offset of the query will be used.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-time-dayofweek.html#query-functions-time-dayofweek-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-time-dayofweek.html#query-functions-time-dayofweek-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     time:dayOfWeek("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     time:dayOfWeek(field="value")
> 
> These examples show basic structure only.

### [`time:dayOfWeek()`](functions-time-dayofweek.html "time:dayOfWeek\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Day of Week From Timestamp

**Get the day of week from a timestamp using the[`time:dayOfWeek()`](functions-time-dayofweek.html "time:dayOfWeek\(\)") function **

##### Query

logscale
    
    
    time:dayOfWeek(timestamp, as=weekday)

##### Introduction

In this example, the [`time:dayOfWeek()`](functions-time-dayofweek.html "time:dayOfWeek\(\)") function is used to extract the day from a specific timestamp `2025-08-27 08:51:51.000`, demonstrating how to get the weekday value from a datetime. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         time:dayOfWeek(timestamp, as=weekday)

Extracts the day of the week from the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named weekday. If the [_`as`_](functions-time-dayofweek.html#query-functions-time-dayofweek-as) parameter is not specified, the result is returned in a field named _dayOfWeek as default. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the day of the week from a timestamp, which is useful for analyzing event patterns across different days of the week. 

This query is useful, for example, to analyze weekly patterns, group events by weekday, or identify activity trends within weeks. 

Sample output from the incoming example data: 

@timestamp| weekday  
---|---  
2025-08-27 08:51:51.000| 3  
  
The result shows how the [`time:dayOfWeek()`](functions-time-dayofweek.html "time:dayOfWeek\(\)") function extracts the day of the week (in this case `3`) from the timestamp, indicating that August 27, 2025, is a Wednesday. 

For visualizing this data, consider using a Bar Chart widget to show event counts by day of week, or a Heat Map widget to display activity patterns across weekdays. The [`time:dayOfWeek()`](functions-time-dayofweek.html "time:dayOfWeek\(\)") function is often used with other time functions like [`time:month()`](functions-time-month.html "time:month\(\)") and [`time:year()`](functions-time-year.html "time:year\(\)") for complete date analysis.
