# eventSize() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-eventsize.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`eventSize()`](functions-eventsize.html "eventSize\(\)")

Determines the number of bytes that this event internally uses in disk storage for the values, not counting the bytes for storing the field names. This does not include the RAM usage of an event during a query, implying that aggregated events will have a size of zero. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-eventsize.html#query-functions-eventsize-as)|  string| optional[a] | `_eventSize`|  Name of output field.   
[a] Optional parameters use their default value unless explicitly set.  
  
### Note

The [`eventSize()`](functions-eventsize.html "eventSize\(\)") function must be used before any aggregate function, otherwise the event size will not be returned as zero. 

### [`eventSize()`](functions-eventsize.html "eventSize\(\)") Examples

Click + next to an example below to get the full details.

#### Search for Events by Size in Repository

**Search for events of a certain size in a repository using[`eventSize()`](functions-eventsize.html "eventSize\(\)") function **

##### Query

logscale
    
    
    eventSize()
    | _eventSize > 10000

##### Introduction

The [`eventSize()`](functions-eventsize.html "eventSize\(\)") function is used to search for events depending on the internal disk storage usages. The function augments the event data with the event size information. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         eventSize()

Determines the number of bytes that events internally use in disk storage for the values (not counting the bytes for storing the field names), and returns the results in a field named _eventSize. 

  3. logscale
         
         | _eventSize > 10000

Searches for events that take up more than 10000 bytes in internal disk storage usage. Notice that you cannot do a direct comparison, as the function augments the event data with the event size information, rather than returning data. 

  4. Event Result set.




##### Summary and Results

The query is used to get an overview of the disk storage usage of the different events and in this example filter on the largest ones. A high disk storage usage can cause performance issues, depending on the time range. 

#### Track Event Size Within a Repository

**Calculate the event size and report the relative size statistics for each event using[`eventSize()`](functions-eventsize.html "eventSize\(\)") function **

##### Query

logscale
    
    
    eventSize(as=eventSize)
    |timeChart(function=[max(eventSize),percentile(field=eventSize,percentiles=[50,75,90,99])])

##### Introduction

This query shows how statistical information about events can first be determined, and then converted into a graph that shows the relative sizes. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         eventSize(as=eventSize)

Extracts the information about the size of each individual event using the [`eventSize()`](functions-eventsize.html "eventSize\(\)") function. 

  3. logscale
         
         |timeChart(function=[max(eventSize),percentile(field=eventSize,percentiles=[50,75,90,99])])

Calculates the [`percentile()`](functions-percentile.html "percentile\(\)") for the eventSize field and determines which filesize is above 50%,75%, and 90,99% of the overall event set, then finds the maximum size for the specified field over a set of events, and displays the returned results in a timechart. 

  4. Event Result set.




##### Summary and Results

The query is used to show how statistical information about events can first be determined, and then converted into a graph that shows the relative sizes.
