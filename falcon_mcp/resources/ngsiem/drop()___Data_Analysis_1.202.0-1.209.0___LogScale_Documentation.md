# drop() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-drop.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Sep 16, 2025

## [`drop()`](functions-drop.html "drop\(\)")

Removes specified fields from each event. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`fields`_](functions-drop.html#query-functions-drop-fields)[a]| array of strings| required |  |  The names of the fields to discard.   
[a] The parameter name [_`fields`_](functions-drop.html#query-functions-drop-fields) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`fields`_](functions-drop.html#query-functions-drop-fields) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     drop(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     drop(fields=["value"])
> 
> These examples show basic structure only.

### [`drop()`](functions-drop.html "drop\(\)") Syntax Examples

Remove specific field from event set: 

This example drops the field f1 from the event set. 

logscale
    
    
    drop(f1)

If input data was `f1=a`, `f2=b`, `f3=c`, it would return: 

f2| f3  
---|---  
b| c  
  
Remove multiple fields from event set: 

This example drops the fields f2 and f3 from the event set. 

logscale
    
    
    drop([f2, f3])

If input data was `f1=a`, `f2=b`, `f3=c`, it would return: 

f1  
---  
a  
  
### [`drop()`](functions-drop.html "drop\(\)") Examples

Click + next to an example below to get the full details.

#### Drop Attributes, Columns/Fields From Result Set - Example 1

**Drop a single field from a result set using the[`drop()`](functions-drop.html "drop\(\)") function **

##### Query

logscale
    
    
    drop(header)

##### Introduction

In this example, the [`drop()`](functions-drop.html "drop\(\)") function is used to remove the header field from result set. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         drop(header)

Drops a single field named header. 

  3. Event Result set.




##### Summary and Results

The query is used to remove data during ingest, in this example removing a field. Removal of fields are useful if you have created fields in sub-searches (extracted some values in new fields during the filtering process) that are no longer needed in the final result set. If you want to drop an entire event, it is possible to use the [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function. 

#### Drop Attributes, Columns/Fields From Result Set - Example 2

**Drop two fields from a result set using the[`drop()`](functions-drop.html "drop\(\)") function **

##### Query

logscale
    
    
    drop([header,value])

##### Introduction

In this example, the [`drop()`](functions-drop.html "drop\(\)") function is used to remove the fields header and value from result set. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         drop([header,value])

Drops both the field named header and the field named value. 

  3. Event Result set.




##### Summary and Results

The query is used to remove data during ingest, in this example removing more fields. Removal of fields are useful if you have created fields in sub-searches (extracted some values in new fields during the filtering process) that are no longer needed in the final result set. If you want to drop an entire event, it is possible to use the [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function. 

#### Drop Multiple Fields from Events

**Remove multiple fields from all events using an array and the[`drop()`](functions-drop.html "drop\(\)") function **

##### Query

logscale
    
    
    drop([header,value])

##### Introduction

In this example, the [`drop()`](functions-drop.html "drop\(\)") function is used to remove both the header and value fields from all events in the dataset using an array syntax. 

Example incoming data might look like this: 

@timestamp| header| message| status| value| user_id  
---|---|---|---|---|---  
2025-09-15T10:00:00Z| HTTP/1.1| User login successful| 200| temp_data| user123  
2025-09-15T10:00:01Z| HTTP/1.1| File uploaded| 201| cache_info| user456  
2025-09-15T10:00:02Z| HTTP/2.0| Authentication failed| 401| debug_val| user789  
2025-09-15T10:00:03Z| HTTP/1.1| Data retrieved| 200| session_id| user123  
2025-09-15T10:00:04Z| HTTP/2.0| Connection timeout| 408| retry_count| user456  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         drop([header,value])

Removes both the header and value fields from all events using array syntax. The [`drop()`](functions-drop.html "drop\(\)") function accepts an array of field names enclosed in square brackets, allowing multiple fields to be eliminated simultaneously in a single operation. 

  3. Event Result set.




##### Summary and Results

The query is used to remove multiple fields (header and value) from all events in the dataset in a single operation. 

This query is useful, for example, to clean up log data by removing multiple redundant fields at once, eliminate several sensitive or temporary fields before data export, or reduce data volume efficiently by dropping multiple unnecessary metadata fields simultaneously. 

Sample output from the incoming example data: 

@timestamp| message| status| user_id  
---|---|---|---  
2025-09-15T10:00:00Z| User login successful| 200| user123  
2025-09-15T10:00:01Z| File uploaded| 201| user456  
2025-09-15T10:00:02Z| Authentication failed| 401| user789  
2025-09-15T10:00:03Z| Data retrieved| 200| user123  
2025-09-15T10:00:04Z| Connection timeout| 408| user456  
  
Note that once fields are dropped, they cannot be recovered in subsequent operations within the same query. Both the header and value fields are completely removed from all events. Using array syntax is more efficient than multiple separate [`drop()`](functions-drop.html "drop\(\)") operations. 

#### Drop Single Field from Events

**Remove the header field from all events using the[`drop()`](functions-drop.html "drop\(\)") function **

##### Query

logscale
    
    
    drop(header)

##### Introduction

In this example, the [`drop()`](functions-drop.html "drop\(\)") function is used to remove the header field from all events in the dataset. 

Example incoming data might look like this: 

@timestamp| header| message| status| user_id  
---|---|---|---|---  
2025-09-15T10:00:00Z| HTTP/1.1| User login successful| 200| user123  
2025-09-15T10:00:01Z| HTTP/1.1| File uploaded| 201| user456  
2025-09-15T10:00:02Z| HTTP/2.0| Authentication failed| 401| user789  
2025-09-15T10:00:03Z| HTTP/1.1| Data retrieved| 200| user123  
2025-09-15T10:00:04Z| HTTP/2.0| Connection timeout| 408| user456  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         drop(header)

Removes the header field from all events. The [`drop()`](functions-drop.html "drop\(\)") function permanently eliminates the specified field from the event data, reducing the amount of data stored and processed in subsequent operations. 

  3. Event Result set.




##### Summary and Results

The query is used to remove the header field from all events in the dataset. 

This query is useful, for example, to clean up log data by removing redundant protocol information, eliminate sensitive fields before sharing data, or reduce data volume by dropping unnecessary metadata fields. 

Sample output from the incoming example data: 

@timestamp| message| status| user_id  
---|---|---|---  
2025-09-15T10:00:00Z| User login successful| 200| user123  
2025-09-15T10:00:01Z| File uploaded| 201| user456  
2025-09-15T10:00:02Z| Authentication failed| 401| user789  
2025-09-15T10:00:03Z| Data retrieved| 200| user123  
2025-09-15T10:00:04Z| Connection timeout| 408| user456  
  
Note that once a field is dropped, it cannot be recovered in subsequent operations within the same query. The header field is completely removed from all events.
