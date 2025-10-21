# selectFromMin() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-selectfrommin.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`selectFromMin()`](functions-selectfrommin.html "selectFromMin\(\)")

Identifies the event with the minimum value in a specified field and returns selected fields from that event. 

The resulting event contains only the fields specified in the [_`include`_](functions-selectfrommin.html#query-functions-selectfrommin-include) parameter. 

If multiple events share the same minimum value, the [`selectFromMin()`](functions-selectfrommin.html "selectFromMin\(\)") function returns one of those events randomly (non-deterministic way). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`field`_](functions-selectfrommin.html#query-functions-selectfrommin-field)[a]| string| required |  |  The name of the field that is used to find the minimum value.   
[_`include`_](functions-selectfrommin.html#query-functions-selectfrommin-include)|  array of strings| required |  |  The names of the fields to include in the generated event.   
[a] The parameter name [_`field`_](functions-selectfrommin.html#query-functions-selectfrommin-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-selectfrommin.html#query-functions-selectfrommin-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     selectFromMin("value",include=["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     selectFromMin(field="value",include=["value"])
> 
> These examples show basic structure only.

### [`selectFromMin()`](functions-selectfrommin.html "selectFromMin\(\)") Syntax Examples

Find the first value of a field x (and when that value was from): 

logscale
    
    
    selectFromMin(@timestamp, include=[x, @timestamp])

This selects the event with minimum value of [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) that also contains the specified field x, and returns an event with fields [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) and x only. 

### [`selectFromMin()`](functions-selectfrommin.html "selectFromMin\(\)") Examples

Click + next to an example below to get the full details.

#### Find Oldest (First) Value of Field X

**Find the oldest (first) value of field X using the[`selectFromMin()`](functions-selectfrommin.html "selectFromMin\(\)") function **

##### Query

logscale
    
    
    selectFromMin(@timestamp, include=[x, @timestamp])

##### Introduction

In this example, the [`selectFromMin()`](functions-selectfrommin.html "selectFromMin\(\)") function is used to find the oldest (first) value of the field x and return the timestamp when that value was recorded. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         selectFromMin(@timestamp, include=[x, @timestamp])

Sorts all events by timestamp, then selects the event in field x with the oldest (lowest) timestamp, returning only the specified fields x and @timestamp. 

In this example, [`selectFromMin()`](functions-selectfrommin.html "selectFromMin\(\)") filters for the "minimum value" of @timestamp, and finds the event with the oldest/first timestamp in the event set that also contains the specified field x. Timestamps are typically stored as numerical values (often in Unix epoch format), where lower numbers represent older times. 

The [_`include`_](functions-selectfrommin.html#query-functions-selectfrommin-include) parameter is used to specify which fields to include in the output. 

  3. Event Result set.




##### Summary and Results

The query is used to find the oldest value of field x by selecting the event with the lowest (oldest) timestamp value. 

Using this query is an efficient way to find the first value since it does not require sorting all results or using other aggregation functions - the query directly selects the oldest matching event.
