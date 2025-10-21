# slidingWindow() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-slidingwindow.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`slidingWindow()`](functions-slidingwindow.html "slidingWindow\(\)")

The [`slidingWindow()`](functions-slidingwindow.html "slidingWindow\(\)") function applies an aggregation to a moving window of a specified number of events in a sequence. It is useful for calculating metrics over a fixed number of recent events, allowing for trend analysis and smoothing of data. For aggregating sliding windows based on time series span, see [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") function. 

For more information about sequence functions and combined usage, see [Sequence Query Functions](functions-sequence.html "Sequence Query Functions"). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`current`_](functions-slidingwindow.html#query-functions-slidingwindow-current)|  enum| optional[a] | [`include`](functions-slidingwindow.html#query-functions-slidingwindow-current-option-include)|  Controls whether to include the current event in the accumulation.   
|  |  | **Values**  
|  |  | [`exclude`](functions-slidingwindow.html#query-functions-slidingwindow-current-option-exclude)| Exclude current event in the accumulation  
|  |  | [`include`](functions-slidingwindow.html#query-functions-slidingwindow-current-option-include)| Include current event in the accumulation  
[ _`events`_](functions-slidingwindow.html#query-functions-slidingwindow-events)|  integer| required |  |  The number of events in each window.   
|  | **Minimum**| `1`| 1 event  
|  | **Maximum**| [`1000`](functions-slidingwindow.html#query-functions-slidingwindow-events-max-1000)| 1000 events  
[ _`function`_](functions-slidingwindow.html#query-functions-slidingwindow-function)[b]| array of aggregate functions| required |  |  The aggregator function(s) to apply to each window. It only accepts functions that output a maximum of one single event.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`function`_](functions-slidingwindow.html#query-functions-slidingwindow-function) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`function`_](functions-slidingwindow.html#query-functions-slidingwindow-function) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     slidingWindow("value",events="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     slidingWindow(function="value",events="value")
> 
> These examples show basic structure only.

### [`slidingWindow()`](functions-slidingwindow.html "slidingWindow\(\)") Function Operation

### Note

  * The [`slidingWindow()`](functions-slidingwindow.html "slidingWindow\(\)") function must be used after an aggregator function (for example, [`head()`](functions-head.html "head\(\)"), [`sort()`](functions-sort.html "sort\(\)"), [`bucket()`](functions-bucket.html "bucket\(\)"), [`groupBy()`](functions-groupby.html "groupBy\(\)")` timeChart()`) to ensure event ordering, as the [`accumulate()`](functions-accumulate.html "accumulate\(\)") function requires a specific order to calculate cumulative values correctly. 

  * Only functions (for example, [`sum()`](functions-sum.html "sum\(\)"), [`avg()`](functions-avg.html "avg\(\)"), [`count()`](functions-count.html "count\(\)")) that output a single event can be used in the sub-aggregation because the [`slidingWindow()`](functions-slidingwindow.html "slidingWindow\(\)") function needs a single value to add to its running total for each event. 




### [`slidingWindow()`](functions-slidingwindow.html "slidingWindow\(\)") Examples

Click + next to an example below to get the full details.

#### Detect Continuously Upwards Going Trend

**Detect continuously upwards going trend using the[`slidingWindow()`](functions-slidingwindow.html "slidingWindow\(\)") function combined with [`neighbor()`](functions-neighbor.html "neighbor\(\)") **

##### Query

logscale
    
    
    head()
    | neighbor(value, prefix=prev)
    | change := value - prev.value
    | slidingWindow(
        [
             {change >= 0 | count(as=positiveTrend)},
             {change < 0  | count(as=negativeTrend)}
        ],
        events=2
        )
    | positiveTrend >= 2

##### Introduction

In this example, the [`slidingWindow()`](functions-slidingwindow.html "slidingWindow\(\)") function combined with [`neighbor()`](functions-neighbor.html "neighbor\(\)") is used to detect continuously upwards going trend. It looks for sequences where the value is consistently increasing or staying the same over at least two consecutive measurements. 

Note that sequence functions must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

value  
---  
3  
5.5  
4  
6  
10  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         head()

Selects the oldest events ordered by time. 

  3. logscale
         
         | neighbor(value, prefix=prev)

Creates a new field named prev.value containing the value from the previous event. 

  4. logscale
         
         | change := value - prev.value

Calculates the change between the current value and the previous value, and assigns the returned results to a field named change. 

  5. logscale
         
         | slidingWindow(
             [
                  {change >= 0 | count(as=positiveTrend)},
                  {change < 0  | count(as=negativeTrend)}
             ],
             events=2
             )

Creates a sliding window of 2 events. Within each window, it counts changes equal to zero or higher (positive or zero changes) and returns the results in a field named positiveTrend, and then also counts the negative changes and returns the results in a field named negativeTrend. 

  6. logscale
         
         | positiveTrend >= 2

Filters for windows where there are at least 2 positive (or zero) changes. 

  7. Event Result set.




##### Summary and Results

The query is used to detect a continuous upwards trend in a series of values. The query can be used to monitor system metrics for consistent increases (for example, memory usage, CPU load) and to identify potential anomalies in time-series data. 

Sample output from the incoming example data: 

value| positiveTrend| negativeTrend| change| prev.value  
---|---|---|---|---  
10| 2| 0| 4| 6
