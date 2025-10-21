# time:year() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-time-year.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`time:year()`](functions-time-year.html "time:year\(\)")

Gets the year of a timestamp field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-time-year.html#query-functions-time-year-as)|  string| optional[a] | `_year`|  The name of the output field.   
[_`field`_](functions-time-year.html#query-functions-time-year-field)[b]| string| optional[[a]](functions-time-year.html#ftn.table-functions-time-year-optparamfn) | `@timestamp`|  The name of the input field.   
[_`timezone`_](functions-time-year.html#query-functions-time-year-timezone)|  string| optional[[a]](functions-time-year.html#ftn.table-functions-time-year-optparamfn) |  |  The time offset to use, for example, `-01:00`. If not specified, the query's offset will be used.   
[_`timezoneField`_](functions-time-year.html#query-functions-time-year-timezonefield)|  string| optional[[a]](functions-time-year.html#ftn.table-functions-time-year-optparamfn) | `@timezone`|  The name of the field containing the timezone to use, if not specified the query's timezone will be used. This is ignored if the timezone parameter is passed as well. If this is not defined the timezone offset of the query will be used.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-time-year.html#query-functions-time-year-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-time-year.html#query-functions-time-year-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     time:year("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     time:year(field="value")
> 
> These examples show basic structure only.

### [`time:year()`](functions-time-year.html "time:year\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Year From Timestamp

**Get the year from a timestamp using the[`time:year()`](functions-time-year.html "time:year\(\)") function **

##### Query

logscale
    
    
    time:year(timestamp, as=year)

##### Introduction

In this example, the [`time:year()`](functions-time-year.html "time:year\(\)") function is used to extract the year from a specific timestamp `2025-08-27 08:51:51.312`, demonstrating how to get the year value from a datetime. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         time:year(timestamp, as=year)

Extracts the year from the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named year. If the [_`as`_](functions-time-year.html#query-functions-time-year-as) parameter is not specified, the result is returned in a field named _year as default. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the year from a timestamp, which is useful for analyzing events across different years. 

This query is useful, for example, to analyze yearly patterns, group events by year, or investigate long-term trends. 

Sample output from the incoming example data: 

@timestamp| year  
---|---  
2025-08-27 08:51:51.312| 2025  
  
The result shows how the [`time:year()`](functions-time-year.html "time:year\(\)") function extracts the year (in this case `2025`) from the timestamp. 

For visualizing this data, consider using a Bar Chart widget to show event distribution across years, or a Line Chart widget to display trends over multiple years. The [`time:year()`](functions-time-year.html "time:year\(\)") function is often used with other time functions like [`time:month()`](functions-time-month.html "time:month\(\)") and [`time:dayOfYear()`](functions-time-dayofyear.html "time:dayOfYear\(\)") for complete date analysis.
