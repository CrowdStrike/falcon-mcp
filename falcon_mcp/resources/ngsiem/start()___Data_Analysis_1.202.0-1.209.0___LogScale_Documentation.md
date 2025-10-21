# start() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-start.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Jun 10, 2025

## [`start()`](functions-start.html "start\(\)")

The [`start()`](functions-start.html "start\(\)") function assigns a timestamp to an output field specified by the [_`as`_](functions-start.html#query-functions-start-as) parameter. This timestamp represents the beginning of the search time interval in milliseconds since January 1, 1970 (UTC). 

For live queries (where the search time interval is forever moving), [`start()`](functions-start.html "start\(\)") equals the current time minus the search interval. 

For subqueries in [`defineTable()`](functions-definetable.html "defineTable\(\)") or joins, [`start()`](functions-start.html "start\(\)") equals the start time of the subquery's search interval. 

### Note

The [`start()`](functions-start.html "start\(\)") function is not compatible with parser operations because parsers do not use search intervals. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-start.html#query-functions-start-as)[a]| string| optional[b] | `_start`|  Name of output field.   
[a] The parameter name [_`as`_](functions-start.html#query-functions-start-as) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`as`_](functions-start.html#query-functions-start-as) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     start("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     start(as="value")
> 
> These examples show basic structure only.

### [`start()`](functions-start.html "start\(\)") Syntax Examples

Assign s the value of [`start()`](functions-start.html "start\(\)"): 

logscale
    
    
    s := start()

Use [`start()`](functions-start.html "start\(\)") in an assignment: 

logscale
    
    
    isOld := (@timestamp - start()) < 1000

### [`start()`](functions-start.html "start\(\)") Examples

Click + next to an example below to get the full details.

#### Search Relative Time to Query Execution

**Writing a query that is executed against a time range relative to when the query is executed using the[`start()`](functions-start.html "start\(\)") function **

##### Query

logscale
    
    
    test(@timestamp < (start() + (30*24*60*60*1000)))

##### Introduction

In this example, the` start()` function is used to test if the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field is less than (earlier than) the start time plus `30` days. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         test(@timestamp < (start() + (30*24*60*60*1000)))

Tests whether the @timestamp for an event is less than the start time of the query. The query start time is returned by the [`start()`](functions-start.html "start\(\)") function. 

To work out the relative time, we add the explicit number of milliseconds by calculating the number of milliseconds in the specified number of days, in this case, `30`. 

Time calculation breakdown is as follows: 

30 (days) 

× 24 (hours) 

× 60 (minutes) 

× 60 (seconds) 

× 1000 (milliseconds) 

= 2,592,000,000 milliseconds (30 days) 

  3. Event Result set.




##### Summary and Results

The query is used to filter events that occurred within the first 30 days after the start time. 

The query is a practical way of querying with a relative time from the query execution. The 30 days (and calculation) used in the example could be updated with any time calculation to achieve the required result.
