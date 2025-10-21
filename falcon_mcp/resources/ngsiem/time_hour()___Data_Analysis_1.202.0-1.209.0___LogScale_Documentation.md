# time:hour() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-time-hour.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`time:hour()`](functions-time-hour.html "time:hour\(\)")

Gets the hour (24-hour clock) of a timestamp field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-time-hour.html#query-functions-time-hour-as)|  string| optional[a] | `_hour`|  The name of the output field.   
[_`field`_](functions-time-hour.html#query-functions-time-hour-field)[b]| string| optional[[a]](functions-time-hour.html#ftn.table-functions-time-hour-optparamfn) | `@timestamp`|  The name of the input field.   
[_`timezone`_](functions-time-hour.html#query-functions-time-hour-timezone)|  string| optional[[a]](functions-time-hour.html#ftn.table-functions-time-hour-optparamfn) |  |  The time offset to use, for example, `-01:00`. If not specified, the query's offset will be used.   
[_`timezoneField`_](functions-time-hour.html#query-functions-time-hour-timezonefield)|  string| optional[[a]](functions-time-hour.html#ftn.table-functions-time-hour-optparamfn) | `@timezone`|  The name of the field containing the timezone to use, if not specified the query's timezone will be used. This is ignored if the timezone parameter is passed as well. If this is not defined the timezone offset of the query will be used.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-time-hour.html#query-functions-time-hour-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-time-hour.html#query-functions-time-hour-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     time:hour("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     time:hour(field="value")
> 
> These examples show basic structure only.

### [`time:hour()`](functions-time-hour.html "time:hour\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Hour From Timestamp

**Get the hour from a timestamp using the[`time:hour()`](functions-time-hour.html "time:hour\(\)") function **

##### Query

logscale
    
    
    time:hour(timestamp, as=hour)

##### Introduction

In this example, the [`time:hour()`](functions-time-hour.html "time:hour\(\)") function is used to extract the hour from a specific timestamp `2025-08-27 08:51:51.000`, demonstrating how to get the hour value from a datetime. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         time:hour(timestamp, as=hour)

Extracts the hour from the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named hour. If the [_`as`_](functions-time-hour.html#query-functions-time-hour-as) parameter is not specified, the result is returned in a field named _hour as default. 

  3. Event Result set.




##### Summary and Results

The query is used to extract the hour from a timestamp, which is useful for analyzing event patterns throughout the day. 

This query is useful, for example, to analyze hourly patterns, identify peak activity hours, or group events by time of day. 

Sample output from the incoming example data: 

@timestamp| hour  
---|---  
2025-08-27 08:51:51.000| 8  
  
The result shows how the [`time:hour()`](functions-time-hour.html "time:hour\(\)") function extracts the hour (in this case `8`) from the timestamp, indicating it is 8 AM in 24-hour format. 

For visualizing this data, consider using a Bar Chart widget to show event distribution across hours, or a Heat Map widget to display activity patterns throughout the day. The [`time:hour()`](functions-time-hour.html "time:hour\(\)") function is often used with other time functions like [`time:minute()`](functions-time-minute.html "time:minute\(\)") and [`time:second()`](functions-time-second.html "time:second\(\)") for complete time analysis. 

#### Hourly Data Events

**Summarize events by providing a count of the number of data events per hour using the[`time:hour()`](functions-time-hour.html "time:hour\(\)") function **

##### Query

logscale
    
    
    hr := time:hour(field="@ingesttimestamp")
    |groupBy(hr)

##### Introduction

In this example, the [`time:hour()`](functions-time-hour.html "time:hour\(\)") function is used with [`groupBy()`](functions-groupby.html "groupBy\(\)") to average the count of data events per hour. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         hr := time:hour(field="@ingesttimestamp")

Gets the hour (24-hour clock) of the values in the @ingesttimestamp and returns the results in a new field named `hr`. 

  3. logscale
         
         |groupBy(hr)

Groups the returned results by hr field and provides a count of the number of data events per hour in a _count field. 

  4. Event Result set.




##### Summary and Results

The query is used to average the count of data events per hour. The results can be plotted onto a bar chart.
