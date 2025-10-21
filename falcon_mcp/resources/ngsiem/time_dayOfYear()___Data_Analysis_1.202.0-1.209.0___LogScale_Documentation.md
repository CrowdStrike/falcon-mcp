# time:dayOfYear() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-time-dayofyear.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`time:dayOfYear()`](functions-time-dayofyear.html "time:dayOfYear\(\)")

Gets the day of the year of a timestamp field (from 1 to 365, or 366 in a leap year). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-time-dayofyear.html#query-functions-time-dayofyear-as)|  string| optional[a] | `_dayOfYear`|  The name of the output field.   
[_`field`_](functions-time-dayofyear.html#query-functions-time-dayofyear-field)[b]| string| optional[[a]](functions-time-dayofyear.html#ftn.table-functions-time-dayofyear-optparamfn) | `@timestamp`|  The name of the input field.   
[_`timezone`_](functions-time-dayofyear.html#query-functions-time-dayofyear-timezone)|  string| optional[[a]](functions-time-dayofyear.html#ftn.table-functions-time-dayofyear-optparamfn) |  |  The time offset to use, for example, `-01:00`. If not specified, the query's offset will be used.   
[_`timezoneField`_](functions-time-dayofyear.html#query-functions-time-dayofyear-timezonefield)|  string| optional[[a]](functions-time-dayofyear.html#ftn.table-functions-time-dayofyear-optparamfn) | `@timezone`|  The name of the field containing the timezone to use, if not specified the query's timezone will be used. This is ignored if the timezone parameter is passed as well. If this is not defined the timezone offset of the query will be used.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-time-dayofyear.html#query-functions-time-dayofyear-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-time-dayofyear.html#query-functions-time-dayofyear-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     time:dayOfYear("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     time:dayOfYear(field="value")
> 
> These examples show basic structure only.

### [`time:dayOfYear()`](functions-time-dayofyear.html "time:dayOfYear\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Day of Year From Timestamp

**Get the day of year from a timestamp using the[`time:dayOfYear()`](functions-time-dayofyear.html "time:dayOfYear\(\)") function **

##### Query

logscale
    
    
    time:dayOfYear(timestamp, as=yearday)

##### Introduction

In this example, the [`time:dayOfYear()`](functions-time-dayofyear.html "time:dayOfYear\(\)") function is used to extract the day from a specific timestamp `2025-08-27 08:51:51.000`, demonstrating how to get the day of year value from a datetime. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         time:dayOfYear(timestamp, as=yearday)

Extracts the day of the year from the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named yearday. If the [_`as`_](functions-time-dayofyear.html#query-functions-time-dayofyear-as) parameter is not specified, the result is returned in a field named _dayOfYear as default. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the day of the year from a timestamp, which is useful for analyzing event patterns across the entire year. 

This query is useful, for example, to analyze annual patterns, track yearly progress, or identify seasonal trends. 

Sample output from the incoming example data: 

@timestamp| yearday  
---|---  
2025-08-27 08:51:51.000| 239  
  
The result shows how the [`time:dayOfYear()`](functions-time-dayofyear.html "time:dayOfYear\(\)") function extracts the day of the year (in this case `239`) from the timestamp, indicating it is the 239th day of 2025. 

For visualizing this data, consider using a Line Chart widget to show event patterns across the year, or a Heat Map widget to display activity patterns throughout the year. The [`time:dayOfYear()`](functions-time-dayofyear.html "time:dayOfYear\(\)") function is often used with other time functions like [`time:month()`](functions-time-month.html "time:month\(\)") and [`time:year()`](functions-time-year.html "time:year\(\)") for complete date analysis.
