# time:monthName() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-time-monthname.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`time:monthName()`](functions-time-monthname.html "time:monthName\(\)")

Gets the English name of month of a timestamp field (for example, January). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-time-monthname.html#query-functions-time-monthname-as)|  string| optional[a] | `_monthName`|  The name of the output field.   
[_`field`_](functions-time-monthname.html#query-functions-time-monthname-field)[b]| string| optional[[a]](functions-time-monthname.html#ftn.table-functions-time-monthname-optparamfn) | `@timestamp`|  The name of the input field.   
[_`timezone`_](functions-time-monthname.html#query-functions-time-monthname-timezone)|  string| optional[[a]](functions-time-monthname.html#ftn.table-functions-time-monthname-optparamfn) |  |  The time offset to use, for example, `-01:00`. If not specified, the query's offset will be used.   
[_`timezoneField`_](functions-time-monthname.html#query-functions-time-monthname-timezonefield)|  string| optional[[a]](functions-time-monthname.html#ftn.table-functions-time-monthname-optparamfn) | `@timezone`|  The name of the field containing the timezone to use, if not specified the query's timezone will be used. This is ignored if the timezone parameter is passed as well. If this is not defined the timezone offset of the query will be used.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-time-monthname.html#query-functions-time-monthname-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-time-monthname.html#query-functions-time-monthname-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     time:monthName("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     time:monthName(field="value")
> 
> These examples show basic structure only.

### [`time:monthName()`](functions-time-monthname.html "time:monthName\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Month Name From Timestamp

**Get the name of the month from a timestamp using the[`time:monthName()`](functions-time-monthname.html "time:monthName\(\)") function **

##### Query

logscale
    
    
    time:monthName(timestamp, as=month)

##### Introduction

In this example, the [`time:monthName()`](functions-time-monthname.html "time:monthName\(\)") function is used to extract the month name from a specific timestamp `2025-08-27 08:51:51.312`, demonstrating how to get the month name from a datetime. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         time:monthName(timestamp, as=month)

Extracts the month name from the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named month. If the [_`as`_](functions-time-monthname.html#query-functions-time-monthname-as) parameter is not specified, the result is returned in a field named _monthName as default. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the month name from a timestamp, which is useful for creating human-readable output and reports. 

This query is useful, for example, to generate readable reports, create user-friendly displays, or label data with month names. 

Sample output from the incoming example data: 

@timestamp| month  
---|---  
2025-08-27 08:51:51.312| August  
  
The result shows how the [`time:monthName()`](functions-time-monthname.html "time:monthName\(\)") function extracts the month name (in this case `August`) from the timestamp, returning it as a string value. 

For visualizing this data, consider using a Bar Chart widget to show event counts by month name, or a Table widget to display events with their corresponding month names. The [`time:monthName()`](functions-time-monthname.html "time:monthName\(\)") function is often used with other time functions like [`time:year()`](functions-time-year.html "time:year\(\)") and [`time:dayOfMonth()`](functions-time-dayofmonth.html "time:dayOfMonth\(\)") for complete date analysis.
