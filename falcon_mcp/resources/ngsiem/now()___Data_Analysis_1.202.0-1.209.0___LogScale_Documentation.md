# now() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-now.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`now()`](functions-now.html "now\(\)")

Assign the current time to the field provided by parameter [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters"). 

The time is represented as milliseconds since January 1, 1970 (UTC). In historical queries, the current time is when the query is issued. In live queries, the current time is when [`now()`](functions-now.html "now\(\)") is processed for each event. The value, therefore, depends on where in the query [`now()`](functions-now.html "now\(\)") is placed. If it is placed before the first aggregate function, it is only evaluated the first time the query sees the event. If it is placed after the first aggregate function, it is evaluated continuously, and gives the live value of the current system time, which can divert between LogScale nodes. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-now.html#query-functions-now-as)[a]| string| optional[b] | `_now`|  Name of output field.   
[a] The parameter name [_`as`_](functions-now.html#query-functions-now-as) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`as`_](functions-now.html#query-functions-now-as) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     now("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     now(as="value")
> 
> These examples show basic structure only.

### [`now()`](functions-now.html "now\(\)") Examples

Click + next to an example below to get the full details.

#### Assign Current Time of Search Time Interval to Field

**Assign the current time of the search time interval to a field using the[`now()`](functions-now.html "now\(\)") function in a comparison **

##### Query

logscale
    
    
    isOld := (now()-@timestamp) > 1000

##### Introduction

In this example, the [`now()`](functions-now.html "now\(\)") function is used to compare the difference between the end time and the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field to determine if an event is "old" (more than 1000 milliseconds old). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         isOld := (now()-@timestamp) > 1000

Returns results where the current time minus the ingestion timestamp are greater than `1000`, and assigns the returned results to a new field named isOld. 

In more details: [`now()`](functions-now.html "now\(\)") returns the end time of the search interval. [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) is the timestamp of the individual event.` (end()-@timestamp)` calculates the difference between these two times, giving the age of the event relative to the end of the search interval. This difference is compared to `1000` milliseconds (1 second). If the difference is greater than `1000` milliseconds, isOld will be set to `true`; otherwise, it will be `false`. 

  3. Event Result set.




##### Summary and Results

The query is used to quickly identifying events that are more than 1 second older than the end of the search interval. Assigning current time of search time interval to a field is useful when, for example, searching for security events. When running a query, the events you are searching do not know the span of the search (the system just returns a list of the events in the given time interval), but you might want to show the relative time of the event timestamp compared to the search window. 

For example, if you search of a bunch of events that happened yesterday and you are searching from `yesterday 00:00 to 23:59`, you then want to calculate '3 hours before' or even '2s before' because when searching for security events that time difference may be important. 

#### Process Current Time in Live Queries

**Process current time in live queries using the[`now()`](functions-now.html "now\(\)") function **

##### Query

logscale
    
    
    curr := now()

##### Introduction

The now() function is used in live queries to process the current time for each event. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         curr := now()

Processes current time for each event and returns the timestamps in a field named curr field. It records when events occur. The timestamp represents milliseconds. 

  3. Event Result set.




##### Summary and Results

The query is used in live queries to process the current time for each event. 

Note that in live queries, this query returns timestamps based on the [`now()`](functions-now.html "now\(\)") function's location: 

  * Before first aggregate function: Returns the initial event processing timestamp (it is only evaluated the first time the query sees the event). 

  * After first aggregate function: Returns continuously updated timestamps from each LogScale node (it gives the live value of the current system time, which can divert between LogScale nodes when [`now()`](functions-now.html "now\(\)") is placed after the first aggregate function). 




The [`now()`](functions-now.html "now\(\)") function and capturing current timestamps is, for example, useful in security contexts for incident response timing, threat detection timestamps and security event correlation.
