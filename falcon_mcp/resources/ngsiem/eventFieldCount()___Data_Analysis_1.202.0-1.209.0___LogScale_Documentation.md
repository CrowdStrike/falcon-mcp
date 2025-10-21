# eventFieldCount() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-eventfieldcount.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`eventFieldCount()`](functions-eventfieldcount.html "eventFieldCount\(\)")

Computes the number of fields that this event uses internally for the values. Tags are not fields in most cases. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-eventfieldcount.html#query-functions-eventfieldcount-as)|  string| optional[a] | `_eventFieldCount`|  Name of output field.   
[a] Optional parameters use their default value unless explicitly set.  
  
### Note

The [`eventFieldCount()`](functions-eventfieldcount.html "eventFieldCount\(\)") function must be used before any aggregate function, otherwise the field count will not be returned. 

### [`eventFieldCount()`](functions-eventfieldcount.html "eventFieldCount\(\)") Examples

Click + next to an example below to get the full details.

#### Search For Events by Number of Fields in Repository 

**Search for events with a certain number of fields in a repository using[`eventFieldCount()`](functions-eventfieldcount.html "eventFieldCount\(\)") function **

##### Query

logscale
    
    
    eventFieldCount()
    | _eventFieldCount <  6

##### Introduction

The [`eventFieldCount()`](functions-eventfieldcount.html "eventFieldCount\(\)") function is used to search for events depending on the number of fields on the event. The [`eventFieldCount()`](functions-eventfieldcount.html "eventFieldCount\(\)") function augments the event data with the event field count information. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         eventFieldCount()

Determines the number of fields that events has, and returns the results in a field named _eventFieldCount. 

  3. logscale
         
         | _eventFieldCount <  6

Searches for events that has fewer than 6 fields. Notice that you cannot do a direct comparison, as the function augments the event data with the event field count information, rather than returning data. 

  4. Event Result set.




##### Summary and Results

The query is used to get an overview of the event with a low field count.
