# time:month() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-time-month.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`time:month()`](functions-time-month.html "time:month\(\)")

Gets the month of a timestamp field. (from 1 to 12) 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-time-month.html#query-functions-time-month-as)|  string| optional[a] | `_month`|  The name of the output field.   
[_`field`_](functions-time-month.html#query-functions-time-month-field)[b]| string| optional[[a]](functions-time-month.html#ftn.table-functions-time-month-optparamfn) | `@timestamp`|  The name of the input field.   
[_`timezone`_](functions-time-month.html#query-functions-time-month-timezone)|  string| optional[[a]](functions-time-month.html#ftn.table-functions-time-month-optparamfn) |  |  The time offset to use, for example, `-01:00`. If not specified, the query's offset will be used.   
[_`timezoneField`_](functions-time-month.html#query-functions-time-month-timezonefield)|  string| optional[[a]](functions-time-month.html#ftn.table-functions-time-month-optparamfn) | `@timezone`|  The name of the field containing the timezone to use, if not specified the query's timezone will be used. This is ignored if the timezone parameter is passed as well. If this is not defined the timezone offset of the query will be used.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-time-month.html#query-functions-time-month-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-time-month.html#query-functions-time-month-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     time:month("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     time:month(field="value")
> 
> These examples show basic structure only.

### [`time:month()`](functions-time-month.html "time:month\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Month From Timestamp

**Get the month from a timestamp using the[`time:month()`](functions-time-month.html "time:month\(\)") function **

##### Query

logscale
    
    
    time:month(timestamp, as=month)

##### Introduction

In this example, the [`time:month()`](functions-time-month.html "time:month\(\)") function is used to extract the month from a specific timestamp `2025-08-27 08:51:51.312`, demonstrating how to get the month value from a datetime. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         time:month(timestamp, as=month)

Extracts the month from the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named month. If the [_`as`_](functions-time-month.html#query-functions-time-month-as) parameter is not specified, the result is returned in a field named _month as default. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the month from a timestamp, which is useful for analyzing events at a monthly level. 

This query is useful, for example, to analyze monthly patterns, group events by month, or investigate seasonal trends throughout the year. 

Sample output from the incoming example data: 

@timestamp| month  
---|---  
2025-08-27 08:51:51.312| 8  
  
The result shows how the [`time:month()`](functions-time-month.html "time:month\(\)") function extracts the month (in this case `8`) from the timestamp, indicating August (the eighth month of the year). 

For visualizing this data, consider using a Bar Chart widget to show event distribution across months, or a Heat Map widget to display activity patterns throughout the year. The [`time:month()`](functions-time-month.html "time:month\(\)") function is often used with other time functions like [`time:year()`](functions-time-year.html "time:year\(\)") and [`time:dayOfMonth()`](functions-time-dayofmonth.html "time:dayOfMonth\(\)") for complete date analysis.
