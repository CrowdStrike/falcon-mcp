# time:dayOfMonth() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-time-dayofmonth.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`time:dayOfMonth()`](functions-time-dayofmonth.html "time:dayOfMonth\(\)")

Gets the day of the month of a timestamp field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-time-dayofmonth.html#query-functions-time-dayofmonth-as)|  string| optional[a] | `_dayOfMonth`|  The name of the output field.   
[_`field`_](functions-time-dayofmonth.html#query-functions-time-dayofmonth-field)[b]| string| optional[[a]](functions-time-dayofmonth.html#ftn.table-functions-time-dayofmonth-optparamfn) | `@timestamp`|  The name of the input field.   
[_`timezone`_](functions-time-dayofmonth.html#query-functions-time-dayofmonth-timezone)|  string| optional[[a]](functions-time-dayofmonth.html#ftn.table-functions-time-dayofmonth-optparamfn) |  |  The time offset to use, for example, `-01:00`. If not specified, the query's offset will be used.   
[_`timezoneField`_](functions-time-dayofmonth.html#query-functions-time-dayofmonth-timezonefield)|  string| optional[[a]](functions-time-dayofmonth.html#ftn.table-functions-time-dayofmonth-optparamfn) |  |  The name of the field containing the timezone to use, if not specified the query's timezone will be used. This is ignored if the timezone parameter is passed as well. If this is not defined the timezone offset of the query will be used.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-time-dayofmonth.html#query-functions-time-dayofmonth-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-time-dayofmonth.html#query-functions-time-dayofmonth-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     time:dayOfMonth("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     time:dayOfMonth(field="value")
> 
> These examples show basic structure only.

### [`time:dayOfMonth()`](functions-time-dayofmonth.html "time:dayOfMonth\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Day of Month From Timestamp

**Get the day of month from a timestamp using the[`time:dayOfMonth()`](functions-time-dayofmonth.html "time:dayOfMonth\(\)") function **

##### Query

logscale
    
    
    time:dayOfMonth(timestamp, as=day)

##### Introduction

In this example, the [`time:dayOfMonth()`](functions-time-dayofmonth.html "time:dayOfMonth\(\)") function is used to extract the day from a specific timestamp `2025-08-27 08:51:51.000`, demonstrating how to get the day value from a datetime. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         time:dayOfMonth(timestamp, as=day)

Extracts the day of the month from the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named day. If the [_`as`_](functions-time-dayofmonth.html#query-functions-time-dayofmonth-as) parameter is not specified, the result is returned in a field named _dayOfMonth as default. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the day of the month from a timestamp, which is useful for analyzing event patterns across different days within months. 

This query is useful, for example, to analyze daily patterns, group events by day, or identify activity trends within months. 

Sample output from the incoming example data: 

@timestamp| day  
---|---  
2025-08-27 08:51:51.000| 27  
  
The result shows how the [`time:dayOfMonth()`](functions-time-dayofmonth.html "time:dayOfMonth\(\)") function extracts the day of the month (in this case `27`) from the timestamp, returning it as an integer value. 

For visualizing this data, consider using a Bar Chart widget to show event counts by day of month, or a Heat Map widget to display activity patterns across days. The [`time:dayOfMonth()`](functions-time-dayofmonth.html "time:dayOfMonth\(\)") function is often used with other time functions like [`time:month()`](functions-time-month.html "time:month\(\)") and [`time:year()`](functions-time-year.html "time:year\(\)") for complete date analysis.
