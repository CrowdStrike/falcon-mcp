# selectFromMax() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-selectfrommax.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`selectFromMax()`](functions-selectfrommax.html "selectFromMax\(\)")

Identifies the event with the maximum value in a specified field and returns selected fields from that event. 

The resulting event contains only the fields specified in the [_`include`_](functions-selectfrommax.html#query-functions-selectfrommax-include) parameter. 

If multiple events share the same maximum value, the [`selectFromMax()`](functions-selectfrommax.html "selectFromMax\(\)") function returns one of those events randomly (non-deterministic way). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`field`_](functions-selectfrommax.html#query-functions-selectfrommax-field)[a]| string| required |  |  The name of the field that is used to find the maximum value.   
[_`include`_](functions-selectfrommax.html#query-functions-selectfrommax-include)|  array of strings| required |  |  The names of the fields to include in the generated event.   
[a] The parameter name [_`field`_](functions-selectfrommax.html#query-functions-selectfrommax-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-selectfrommax.html#query-functions-selectfrommax-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     selectFromMax("value",include=["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     selectFromMax(field="value",include=["value"])
> 
> These examples show basic structure only.

### [`selectFromMax()`](functions-selectfrommax.html "selectFromMax\(\)") Examples

Click + next to an example below to get the full details.

#### Find Most Recent (Latest) Value of Field X

**Find the most recent (latest) value of field X using the[`selectFromMax()`](functions-selectfrommax.html "selectFromMax\(\)") function **

##### Query

logscale
    
    
    selectFromMax(@timestamp, include=[x, @timestamp])

##### Introduction

In this example, the [`selectFromMax()`](functions-selectfrommax.html "selectFromMax\(\)") function is used to find the most recent (latest) value of the field x and return the timestamp when that value was recorded. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         selectFromMax(@timestamp, include=[x, @timestamp])

Sorts all events by timestamp, then selects the event in field x with the highest (most recent) timestamp, returning only the specified fields x and @timestamp. 

In this example, [`selectFromMax()`](functions-selectfrommax.html "selectFromMax\(\)") filters for the "maximum value" of @timestamp, and finds the event with the newest/latest timestamp in the event set that also contains the specified field x. Timestamps are typically stored as numerical values (often in Unix epoch format), where larger numbers represent more recent times. 

The [_`include`_](functions-selectfrommax.html#query-functions-selectfrommax-include) parameter is used to specify which fields to include in the output. 

  3. Event Result set.




##### Summary and Results

The query is used to find the most recent value of field x by selecting the event with the highest (most recent) timestamp value. 

Using this query is an efficient way to find the latest value since it does not require sorting all results or using other aggregation functions - the query directly selects the most recent matching event.
