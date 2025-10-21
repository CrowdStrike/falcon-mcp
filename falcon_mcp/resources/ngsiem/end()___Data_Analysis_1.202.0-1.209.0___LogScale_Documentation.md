# end() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-end.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Jun 10, 2025

## [`end()`](functions-end.html "end\(\)")

The [`end()`](functions-end.html "end\(\)") function assigns a timestamp to an output field specified by the [_`as`_](functions-end.html#query-functions-end-as) parameter. This timestamp represents the end of the search time interval in milliseconds since January 1, 1970 (UTC). 

For live queries (where the search time interval is forever moving), [`end()`](functions-end.html "end\(\)") is equivalent to [`now()`](functions-now.html "now\(\)") — that is, the current time. 

For subqueries in [`defineTable()`](functions-definetable.html "defineTable\(\)") or joins, [`end()`](functions-end.html "end\(\)") equals the end time of the subquery's search interval. 

### Note

The [`end()`](functions-end.html "end\(\)") function is not compatible with parser operations because parsers do not use search intervals. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-end.html#query-functions-end-as)[a]| string| optional[b] | `_end`|   
[a] The parameter name [_`as`_](functions-end.html#query-functions-end-as) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`as`_](functions-end.html#query-functions-end-as) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     end("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     end(as="value")
> 
> These examples show basic structure only.

### [`end()`](functions-end.html "end\(\)") Examples

Click + next to an example below to get the full details.

#### Assign End of Search Time Interval to Field - Example 1

**Assign the end of the search time interval to a field using the[`end()`](functions-end.html "end\(\)") function **

##### Query

logscale
    
    
    e := end()

##### Introduction

In this example, the [`end()`](functions-end.html "end\(\)") function is used to assign the end of the search time interval to a field named e. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         e := end()

Assigns the value of end to a new field named e. 

  3. Event Result set.




##### Summary and Results

The query is used to assign the end of the search time interval to a specified field. Assigning end of search time interval to a field is useful when, for example, searching for security events. When doing a query, the events you are searching do not know the span of the search (the system just returns a list of the events in the given time interval), but you might want to show the relative time of the event timestamp compared to the search window. For example, if you search of a bunch of events that happened yesterday and you are searching from `yesterday 00:00 to 23:59`, you then want to calculate '3 hours before' or even '2s before' because when searching for security events that time difference may be important. 

#### Assign End of Search Time Interval to Field - Example 2

**Assign the end of the search time interval to a field using the[`end()`](functions-end.html "end\(\)") function in a comparison **

##### Query

logscale
    
    
    isOld := (end()-@timestamp) > 1000

##### Introduction

In this example, the [`end()`](functions-end.html "end\(\)") is used to compare the difference between the end time and the @timestamp field to determine if an event is "old" (more than 1000 milliseconds old). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         isOld := (end()-@timestamp) > 1000

Returns results where the current time minus the ingestion timestamp are greater than `1000`, and assigns the returned results to a new field named isOld. 

In more details: [`end()`](functions-end.html "end\(\)") returns the end time of the search interval. @timestamp is the timestamp of the individual event.`(end()-@timestamp)` calculates the difference between these two times, giving the age of the event relative to the end of the search interval. This difference is compared to `1000` milliseconds (1 second). If the difference is greater than `1000` milliseconds, isOld will be set to `true`; otherwise, it will be `false`. 

  3. Event Result set.




##### Summary and Results

The query is used to quickly identifying events that are more than 1 second older than the end of the search interval. Assigning end of search time interval to a field is useful when, for example, searching for security events. When doing a query, the events you are searching do not know the span of the search (the system just returns a list of the events in the given time interval), but you might want to show the relative time of the event timestamp compared to the search window. For example, if you search of a bunch of events that happened yesterday and you are searching from `yesterday 00:00 to 23:59`, you then want to calculate '3 hours before' or even '2s before' because when searching for security events that time difference may be important.
