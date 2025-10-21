# slidingTimeWindow() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-slidingtimewindow.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)")

The [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") function applies an aggregation to a moving time-based window of events in a sequence. It is useful for calculating metrics over a fixed time period, allowing for time-based trend analysis and data smoothing. 

The difference between [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") and [`window()`](functions-window.html "window\(\)") is that [`window()`](functions-window.html "window\(\)") spans multiple buckets and accumulates events inside the bucket, whereas [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") does not use buckets, but simply accumulates across the incoming events within a specified span. 

For more information about sequence functions and combined usage, see [Sequence Query Functions](functions-sequence.html "Sequence Query Functions"). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`current`_](functions-slidingtimewindow.html#query-functions-slidingtimewindow-current)|  enum| optional[a] | [`include`](functions-slidingtimewindow.html#query-functions-slidingtimewindow-current-option-include)|  Controls whether to include the current event in the window calculation.   
|  |  | **Values**  
|  |  | [`exclude`](functions-slidingtimewindow.html#query-functions-slidingtimewindow-current-option-exclude)| Exclude current event in window calculation  
|  |  | [`include`](functions-slidingtimewindow.html#query-functions-slidingtimewindow-current-option-include)| Include current event in window calculation  
[ _`function`_](functions-slidingtimewindow.html#query-functions-slidingtimewindow-function)[b]| array of aggregate functions| required |  |  The aggregator function(s) to apply to each time window. It only accepts functions that output at most a single event.   
[_`span`_](functions-slidingtimewindow.html#query-functions-slidingtimewindow-span)|  string| required |  |  The duration of the time window (for example, `1h`, `30m`, `1d`).   
[_`timestampfield`_](functions-slidingtimewindow.html#query-functions-slidingtimewindow-timestampfield)|  string| optional[[a]](functions-slidingtimewindow.html#ftn.table-functions-slidingtimewindow-optparamfn) | `Either @timestamp or @ingestTimestamp depending on what is selected for the query.`|  Specifies the field to use as the timestamp for calculations.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`function`_](functions-slidingtimewindow.html#query-functions-slidingtimewindow-function) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`function`_](functions-slidingtimewindow.html#query-functions-slidingtimewindow-function) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     slidingTimeWindow("value",span="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     slidingTimeWindow(function="value",span="value")
> 
> These examples show basic structure only.

### [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") Function Operation

### Note

  * The [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") function must be used after an aggregator function (for example, [`head()`](functions-head.html "head\(\)"), [`sort()`](functions-sort.html "sort\(\)"), [`bucket()`](functions-bucket.html "bucket\(\)"), [`groupBy()`](functions-groupby.html "groupBy\(\)")` timeChart()`) to ensure event ordering, as the [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") function requires a specific order to calculate cumulative values correctly. 

  * Only functions (for example, [`sum()`](functions-sum.html "sum\(\)"), [`avg()`](functions-avg.html "avg\(\)"), [`count()`](functions-count.html "count\(\)")) that output a single event can be used in the sub-aggregation because the [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") function needs a single value to add to its running total for each event. 

  * The window can contain a maximum of 10000 events. 

  * Events must be sorted in order by timestamp. Unordered or missing timestamps will result in errors. 




### [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") Examples

Click + next to an example below to get the full details.

#### Detect Event A Happening X Times Before Event B Within a Specific Timespan

**Detect event A happening X times before event B within a specific timespan using the[`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") function combined with [`groupBy()`](functions-groupby.html "groupBy\(\)") **

##### Query

logscale
    
    
    head()
    | groupBy(
        key,
        function=slidingTimeWindow(
            [{status="failure" | count(as=failures)}, selectLast(status)],
            span=3s
        )
      )
    | failures >= 3
    | status = "success"

##### Introduction

In this example, the [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") function is used with the [`groupBy()`](functions-groupby.html "groupBy\(\)") function to detect event A happening X times before event B within a specific timespan. 

The query will detect instances where there are 3 or more failed attempts followed by a successful attempt, all occurring within a 3-second window. 

Note that the [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") function must be used after an aggregator function to ensure event ordering. Also note that the events must be sorted in order by timestamp to prevent errors when running the query. It is possible to select any field to use as a timestamp. 

Example incoming data might look like this: 

@timestamp| key| status  
---|---|---  
1451606300200| c| failure  
1451606300400| c| failure  
1451606300600| c| failure  
1451606301000| a| failure  
1451606302000| a| failure  
1451606302200| a| failure  
1451606302300| a| failure  
1451606302400| b| failure  
1451606302500| a| failure  
1451606302600| a| success  
1451606303200| b| failure  
1451606303300| c| success  
1451606303400| b| failure  
1451606304500| a| failure  
1451606304600| a| failure  
1451606304700| a| failure  
1451606304800| a| success  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         head()

Selects the oldest events ordered by time. 

  3. logscale
         
         | groupBy(
             key,
             function=slidingTimeWindow(
                 [{status="failure" | count(as=failures)}, selectLast(status)],
                 span=3s
             )
           )

Groups the events by a specified key (for example, a user ID or IP address), then creates a sliding time window of 3 seconds (with a span of 3 seconds). 

Furthermore, it filters all the failed attempts where the field status contains the value `failure`, makes a count of all the failed attempts, and returns the results in a field named failures, calculates the timespan of the failures, retrieves the timestamp of the last failure, and selects the status of the last event. 

  4. logscale
         
         | failures >= 3

Filters for windows with 3 or more failures. 

  5. logscale
         
         | status = "success"

Filters for partitions containing the value `success` in the status field. 

  6. Event Result set.




##### Summary and Results

The query is used to detect event A happening X times before event B within a specific timespan. It looks for instances where there were 3 or more failed attempts followed by a successful attempt, all occurring within a 3-second window. Using a sliding time window of 3 seconds, provides a more precise time constraint compared to the usage of [`partition()`](functions-partition.html "partition\(\)") in [Detect Event A Happening X Times Before Event B](https://library.humio.com/examples/examples-partition-groupby-detect-event-a.html). 

The query can be used to detect potential brute force attack patterns within a specific timeframe. Note that the effectiveness of this query depends on the nature of your data and the typical patterns in your system. 

Sample output from the incoming example data: 

key| failures| status  
---|---|---  
a| 5| success  
a| 7| success  
  
#### Detect Two Events Occurring in Quick Succession

**Detect event B occurring quickly after event A using the[`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") function **

##### Query

logscale
    
    
    head()
    | slidingTimeWindow(
        [{event = "A" | count(event, as=countAs)}, selectLast(event)], 
        span=1s
      )
    | countAs > 0
    | event = "B"

##### Introduction

In this example, the [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") function is used to detect event B occurring quickly after event A. 

Note that the [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") function must be used after an aggregator function to ensure event ordering. Also note that the events must be sorted in order by timestamp to prevent errors when running the query. It is possible to select any field to use as a timestamp. 

Example incoming data might look like this: 

@timestamp| event  
---|---  
1451606300500| A  
1451606301000| B  
1451606302000| A  
1451606304000| B  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         head()

Selects the oldest events ordered by time. 

  3. logscale
         
         | slidingTimeWindow(
             [{event = "A" | count(event, as=countAs)}, selectLast(event)], 
             span=1s
           )

Creates a sliding time window of 1 second. Within each window it counts the occurrences of event A, returning the results in a new field named countAs, and selects the event type of the last event in the window. 

  4. logscale
         
         | countAs > 0

Filters for windows where at least one event A occurred. 

  5. logscale
         
         | event = "B"

Checks if the last event in the window is event B. 

  6. Event Result set.




##### Summary and Results

The query is used to detect instances where event B occurs quickly (within 1 second) after event A. The [_`span`_](functions-slidingtimewindow.html#query-functions-slidingtimewindow-span) parameter configures the interval, allowing this to be customized. 

Sample output from the incoming example data: 

countAs| event| @timestamp  
---|---|---  
1| B| 1451606301000  
  
The query is useful for identifying sequences of events that happen in quick succession, which could indicate specific patterns of behavior or system interactions.
