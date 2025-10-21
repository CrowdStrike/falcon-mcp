# eventInternals() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-eventinternals.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`eventInternals()`](functions-eventinternals.html "eventInternals\(\)")

Adds a set of fields describing the storage locations of this event. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`prefix`_](functions-eventinternals.html#query-functions-eventinternals-prefix)|  string| optional[a] | `@`|  Prefix of output fields.   
[a] Optional parameters use their default value unless explicitly set.  
  
### Note

The [`eventInternals()`](functions-eventinternals.html "eventInternals\(\)") function must be used before any aggregate function, otherwise the storage location will not be returned. 

### [`eventInternals()`](functions-eventinternals.html "eventInternals\(\)") Examples

Click + next to an example below to get the full details.

#### Count Events From Each Datasource 

**Count events from each datasource by using[`eventInternals()`](functions-eventinternals.html "eventInternals\(\)") function to add storage location to each event **

##### Query

logscale
    
    
    eventInternals()
    | groupBy([@datasourceId])

##### Introduction

The [`eventInternals()`](functions-eventinternals.html "eventInternals\(\)") function is used to add the storage locations of this event. The [`eventInternals()`](functions-eventinternals.html "eventInternals\(\)") function augments the event data with the event field count information. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         eventInternals()

Adds a @datasourceId field describing the storage locations of the event. 

  3. logscale
         
         | groupBy([@datasourceId])

Groups the events based on the @datasourceId, performs a count of the events and returns the results in a _count field. 

  4. Event Result set.




##### Summary and Results

The query is used to find the number of events per datasource.
