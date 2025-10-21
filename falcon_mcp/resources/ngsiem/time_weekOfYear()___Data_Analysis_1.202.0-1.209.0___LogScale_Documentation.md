# time:weekOfYear() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-time-weekofyear.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`time:weekOfYear()`](functions-time-weekofyear.html "time:weekOfYear\(\)")

Gets the week number within a year of a timestamp (a value from 1 to 53). The week number is as defined by ISO 8601: Weeks start on a Monday and belong to the year which contains Thursday (or, equivalently, contains the majority of the week days). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-time-weekofyear.html#query-functions-time-weekofyear-as)|  string| optional[a] | `_weekOfYear`|  The name of the output field.   
[_`field`_](functions-time-weekofyear.html#query-functions-time-weekofyear-field)[b]| string| optional[[a]](functions-time-weekofyear.html#ftn.table-functions-time-weekofyear-optparamfn) | `@timestamp`|  The name of the input field.   
[_`timezone`_](functions-time-weekofyear.html#query-functions-time-weekofyear-timezone)|  string| optional[[a]](functions-time-weekofyear.html#ftn.table-functions-time-weekofyear-optparamfn) |  |  The time offset to use, for example, `-01:00`. If not specified, the query's offset will be used.   
[_`timezoneField`_](functions-time-weekofyear.html#query-functions-time-weekofyear-timezonefield)|  string| optional[[a]](functions-time-weekofyear.html#ftn.table-functions-time-weekofyear-optparamfn) | `@timezone`|  The name of the field containing the timezone to use, if not specified the query's timezone will be used. This is ignored if the timezone parameter is passed as well. If this is not defined the timezone offset of the query will be used.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-time-weekofyear.html#query-functions-time-weekofyear-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-time-weekofyear.html#query-functions-time-weekofyear-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     time:weekOfYear("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     time:weekOfYear(field="value")
> 
> These examples show basic structure only.

### [`time:weekOfYear()`](functions-time-weekofyear.html "time:weekOfYear\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Week Number From Timestamp

**Get the ISO week number from a timestamp using the[`time:weekOfYear()`](functions-time-weekofyear.html "time:weekOfYear\(\)") function **

##### Query

logscale
    
    
    time:weekOfYear(timestamp, as=week)

##### Introduction

In this example, the [`time:weekOfYear()`](functions-time-weekofyear.html "time:weekOfYear\(\)") function is used to extract the week number from a specific timestamp `2025-08-27 08:51:51.312`, demonstrating how to get the ISO week value from a datetime. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         time:weekOfYear(timestamp, as=week)

Extracts the ISO week number from the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named week. If the [_`as`_](functions-time-weekofyear.html#query-functions-time-weekofyear-as) parameter is not specified, the result is returned in a field named _weekOfYear as default. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the week number from a timestamp, which is useful for analyzing events at a weekly level following international standards. 

This query is useful, for example, to analyze weekly patterns, group events by ISO week, or investigate trends across weeks of the year. 

Sample output from the incoming example data: 

@timestamp| week  
---|---  
2025-08-27 08:51:51.312| 35  
  
The result shows how the [`time:weekOfYear()`](functions-time-weekofyear.html "time:weekOfYear\(\)") function extracts the week number (in this case `35`) from the timestamp, indicating it is the 35th week of 2025 according to ISO 8601 standards. 

For visualizing this data, consider using a Bar Chart widget to show event distribution across weeks, or a Heat Map widget to display activity patterns throughout the year by week. The [`time:weekOfYear()`](functions-time-weekofyear.html "time:weekOfYear\(\)") function is often used with other time functions like [`time:year()`](functions-time-year.html "time:year\(\)") and [`time:dayOfWeek()`](functions-time-dayofweek.html "time:dayOfWeek\(\)") for complete date analysis.
