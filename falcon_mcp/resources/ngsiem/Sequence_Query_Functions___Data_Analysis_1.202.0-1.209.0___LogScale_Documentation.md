# Sequence Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-sequence.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Sequence Query Functions

LogScale's sequence functions enable powerful computations on ordered event data by working with sequences of events and their surrounding context. This page covers the core sequence query functions (accumulate, neighbor, partition, slidingTimeWindow, and slidingWindow), explains key usage restrictions and rules, and demonstrates how to combine these functions to solve complex use cases like calculating cumulative aggregations, detecting changes between events, identifying event patterns, and performing trend analysis. 

LogScale's sequence functions work on a sequence of events. In LogScale, a sequence is any set of events with meaningful order. These sequence functions are used to perform computations that depend on the context of surrounding events. 

LogScale events are not inherently ordered, therefore, sequence functions must be used after an aggregator function to establish an ordering. Except for this restriction, the sequence functions can be used in the same places as regular aggregator functions. 

**Table: Sequence Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`accumulate([current], function)`](functions-accumulate.html "accumulate\(\)")| [_`function`_](functions-accumulate.html#query-functions-accumulate-function)|  |  Applies an aggregation function cumulatively to a sequence of events.   
[`neighbor([direction], [distance], include, [prefix])`](functions-neighbor.html "neighbor\(\)")| [_`include`_](functions-neighbor.html#query-functions-neighbor-include)|  |  Allows access to fields from a single neighboring event in a sequence.   
[`partition(condition, function, [split])`](functions-partition.html "partition\(\)")| [_`function`_](functions-partition.html#query-functions-partition-function)|  |  Splits a sequence of events into multiple partitions based on a condition.   
[`slidingTimeWindow([current], function, span, [timestampfield])`](functions-slidingtimewindow.html "slidingTimeWindow\(\)")| [_`function`_](functions-slidingtimewindow.html#query-functions-slidingtimewindow-function)|  |  Applies an aggregation to a moving time-based window of events in a sequence.   
[`slidingWindow([current], events, function)`](functions-slidingwindow.html "slidingWindow\(\)")| [_`function`_](functions-slidingwindow.html#query-functions-slidingwindow-function)|  |  Applies an aggregation to a moving window of a specified number of events in a sequence.   
  
  


### Using Sequence Query Functions

The following rules and recommendations apply to all the sequence query functions listed in the [Sequence Query Functions](functions-sequence.html#table_functions-sequence "Table: Sequence Query Functions") table: 

  * Sequence functions cannot be used inside the [`stats()`](functions-stats.html "stats\(\)") function alongside other functions that produce multiple events. 

  * Sequence functions must come after an aggregator function (for example, [`bucket()`](functions-bucket.html "bucket\(\)"), [`head()`](functions-head.html "head\(\)"), [`sort()`](functions-sort.html "sort\(\)")) to provide a meaningful order to the events. LogScale recommends using the [`sort()`](functions-sort.html "sort\(\)") function before sequence functions to ensure meaningful event order. 




### Combining Sequence Functions

Sequence functions can be used individually to compute and visualize interesting statistics about events. More importantly, these functions are designed as modular building blocks that can be combined to solve more advanced tasks. 

This section demonstrates how to combine sequence functions to solve complex use cases, showcasing their flexibility and power when used together. The [`head()`](functions-head.html "head\(\)") function is used in the examples to sort events by `@timestamp`. 

For more information on the individual sequence function and more examples, see [`accumulate()`](functions-accumulate.html "accumulate\(\)"), [`slidingWindow()`](functions-slidingwindow.html "slidingWindow\(\)"), [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)"), [`neighbor()`](functions-neighbor.html "neighbor\(\)"), or [`partition()`](functions-partition.html "partition\(\)"). 

#### Calculating an Accumulative Aggregation

The following contains examples of calculating acumulative aggregations. 

##### Base Case:

The [`accumulate()`](functions-accumulate.html "accumulate\(\)") function can be used to calculate a running aggregation. It works with any aggregator that outputs a single event, such as [`sum()`](functions-sum.html "sum\(\)") or [`avg()`](functions-avg.html "avg\(\)"): 

logscale Syntax
    
    
    head() 
    | accumulate(avg(value))

The query is used to calculate the running average of fields. The query calculates moving averages that change as new values arrive. 

For a description of the query, see [Calculate Running Average of Field Values](https://library.humio.com/examples/examples-accumulate-basic.html). 

### Note

For aggregations over a limited number of preceding events or a specific time span, the [`slidingWindow()`](functions-slidingwindow.html "slidingWindow\(\)") and [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)") functions can be used instead of the [`accumulate()`](functions-accumulate.html "accumulate\(\)") function. 

##### Accumulate by Group:

To compute a cumulative aggregation for a specific group (for example, by user), the [`accumulate()`](functions-accumulate.html "accumulate\(\)") function can be used inside the [`groupBy()`](functions-groupby.html "groupBy\(\)") function: 

logscale Syntax
    
    
    head() 
    | groupBy(key, function = accumulate(sum(value)))

The query is used to compute a cumulative aggregation for a specific group. 

For a description of the query, see [Compute Cumulative Aggregation For Specific Group ](https://library.humio.com/examples/examples-accumulate-groupby-example.html). 

##### Accumulate Across Buckets:

A common use case is to accumulate values across time intervals, such as days. This can be achieved by applying the [`accumulate()`](functions-accumulate.html "accumulate\(\)") function after a [`bucket()`](functions-bucket.html "bucket\(\)") or [`timeChart()`](functions-timechart.html "timeChart\(\)") function: 

logscale Syntax
    
    
    timeChart(span=1000ms, function=sum(value)) 
    | accumulate(sum(_sum, as=_accumulated_sum))

The query is used to accumulate values across time intervals/buckets. The query is, for example, useful for tracking cumulative metrics or identifying trends in the data. 

For a description of the query, see [Compute Cumulative Aggregation Across Buckets](https://library.humio.com/examples/examples-accumulate-bucket-example.html). 

##### Partitioned Accumulation:

Accumulations can also be partitioned based on a condition, such as a change in value. This is achieved by combining three functions: 

  * The [`neighbor()`](functions-neighbor.html "neighbor\(\)") function to access values from adjacent events. 

  * The [`partition()`](functions-partition.html "partition\(\)") function to split the sequence of events. 

  * The [`accumulate()`](functions-accumulate.html "accumulate\(\)") function to perform the cumulative calculation within each partition. 




The following shows an example that counts events within partitions defined by changes in the [key](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-fdr-ingest.html) field: 

logscale Syntax
    
    
    head() 
    | neighbor(key, prefix=prev) 
    | partition(accumulate(count()), condition=test(key != prev.key))

The query is used to count events within partitions based on a specific condition. The query is useful for analyzing sequences of events, especially when you want to identify and count consecutive occurrences of a particular attribute in order to identify and analyze patterns or sequences within your data. 

This approach can be extended to use any condition for partitioning, expressed as a`{query}`. 

For a description of the query, see [Count Events Within Partitions Based on Condition](https://library.humio.com/examples/examples-partition-neighbor-accumulation-example.html). 

#### Detecting Changes and Computing Differences

The [`neighbor()`](functions-neighbor.html "neighbor\(\)") function can be effectively used to spot changes or compute differences between events. 

The following shows two examples. 

##### Alerting on Large Increase:

logscale Syntax
    
    
    head() 
    | neighbor(value, prefix=prev) 
    | change := value - prev.value 
    | change > 5

The query is used to detect changes in values and alert on large increase. The query will identify events where the value has increased by more than 5 compared to the previous event. The query is useful for real-time monitoring and alerting systems where you need to quickly identify significant changes in sequential data. It allows for immediate detection of anomalies or important shifts in your data, enabling prompt responses to potential issues or opportunities. 

For a description of the query, see [Detect Changes And Compute Differences Between Events - Example 1](https://library.humio.com/examples/examples-neighbor-changes-example-1.html). 

##### Accumulating Changes:

logscale Syntax
    
    
    head() 
    | neighbor(start, prefix=prev) 
    | duration := start - prev.start 
    | accumulate(sum(duration, as=accumulated_duration))

Given the start time of each step in a process, it calculates duration of each step along with accumulated duration of the full process. 

The query is used to calculate the time difference between consecutive events. The query is useful for analyzing temporal data, to provide insights into process efficiency, system performance over time etc. 

For a description of the query, see [Detect Changes And Compute Differences Between Events - Example 2](https://library.humio.com/examples/examples-neighbor-changes-example-2.html). 

For more information on the individual sequence function and more examples, see [`accumulate()`](functions-accumulate.html "accumulate\(\)"), [`slidingWindow()`](functions-slidingwindow.html "slidingWindow\(\)"), [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)"), [`neighbor()`](functions-neighbor.html "neighbor\(\)"), or [`partition()`](functions-partition.html "partition\(\)"). 

#### Detecting Series

##### Detect Event A Happening X Times Before Event B (Brute Force Attack):

logscale Syntax
    
    
    head() 
    | groupBy(
      key,
      function = partition(
          condition=test(status=="success"),
          split="after",
          [
              { status="failure" 
    | count(as=failures) }, 
              range(@timestamp, as=timespan), 
              max(@timestamp), 
              selectLast(status)
          ]
      )
    )
    | failures >= 3 
    | status = "success"

The query is used to detect instances where there are 3 or more failed attempts followed by a successful attempt. The query can be used to detect a brute force attack where an attacker tries multiple times before succeeding. Note that the effectiveness of this query depends on the nature of your data and the typical patterns in your system. 

For a description of the query, see [Detect Event A Happening X Times Before Event B](https://library.humio.com/examples/examples-partition-groupby-detect-event-a.html). 

##### Detect Event A Happening X Times Before Event B Within a Specific Timespan:

logscale Syntax
    
    
    head() 
    | groupBy(
          key,
          function=slidingTimeWindow(
              [{status="failure" 
    | count(as=failures)}, selectLast(status)],
              span=3s
          )
      ) 
    | failures >= 3 
    | status="success"

The query is used to detect event A happening X times before event B within a specific timespan. It looks for instances where there were 3 or more failed attempts followed by a successful attempt, all occurring within a 3-second window. Using a sliding time window of 3 seconds, provides a more precise time constraint compared to the usage of [`partition()`](functions-partition.html "partition\(\)") in [Detect Event A Happening X Times Before Event B](https://library.humio.com/examples/examples-partition-groupby-detect-event-a.html). The query can be used to detect potential brute force attack patterns within a specific timeframe. Note that the effectiveness of this query depends on the nature of your data and the typical patterns in your system. 

For a description of the query, see [Detect Event A Happening X Times Before Event B Within a Specific Timespan](https://library.humio.com/examples/examples-slidingtimewindow-groupby-detect-event-a.html). 

##### Detect All Occurrences of Event A Before Event B (Brute Force Attack):

logscale Syntax
    
    
    head() 
    | groupBy(
        key,
        function = partition(
            condition=test(status=="success"),
            split="after",
            [
                { status="failure" 
    | count(as=failures) }, 
                range(@timestamp, as=timespan), 
                selectLast(status)
            ]
        )
      ) 
    | failures >= 3 
    | status = "success"

The query is used to detect all occurrences of potential brute force attack patterns within the specified timeframe. It looks for instances where there were 3 or more failed attempts (event A) followed by a successful attempt (event B), regardless of the time between failures. 

For a description of the query, see [Detect All Occurrences of Event A Before Event B](https://library.humio.com/examples/examples-partition-groupby-detect-all-occurrences.html). 

##### Detect Two Events Occurring in Quick Succession:

logscale Syntax
    
    
    head() 
    | slidingTimeWindow(
        [{event = "A" 
    | count(event, as=countAs)} , selectLast(event)], 
        span=1s
      ) 
    | countAs > 0 
    | event = "B"

The query is used to detect instances where event B occurs quickly (within 1 second) after event A. The query is useful for identifying sequences of events that happen in quick succession, which could indicate specific patterns of behavior or system interactions. 

For a description of the query, see [Detect Two Events Occurring in Quick Succession](https://library.humio.com/examples/examples-slidingtimewindow-groupby-detect-quick-succession.html). 

For more information on the individual sequence function and more examples, see [`accumulate()`](functions-accumulate.html "accumulate\(\)"), [`slidingWindow()`](functions-slidingwindow.html "slidingWindow\(\)"), [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)"), [`neighbor()`](functions-neighbor.html "neighbor\(\)"), or [`partition()`](functions-partition.html "partition\(\)"). 

#### Trend And Anomaly Detection

Detect continuously upwards going trend: 

logscale Syntax
    
    
    head() 
    | neighbor(value, prefix=prev) 
    | change := value - prev.value 
    | slidingWindow(
          [
              { change >= 0 
    | count(as=positiveTrend)}, 
              { change < 0  
    | count(as=negativeTrend)}
          ], 
          events=2
      ) 
    | positiveTrend >= 2

The query is used to detect continuously upwards going trend in a series of values. The query can be used to monitor system metrics for consistent increases (for example, memory usage, CPU load) and to identify potential anomalies in time-series data. 

For a description of the query, see [Detect Continuously Upwards Going Trend](https://library.humio.com/examples/examples-slidingwindow-neighbor-trend-detection.html). 

For more information on the individual sequence function and more examples, see [`accumulate()`](functions-accumulate.html "accumulate\(\)"), [`slidingWindow()`](functions-slidingwindow.html "slidingWindow\(\)"), [`slidingTimeWindow()`](functions-slidingtimewindow.html "slidingTimeWindow\(\)"), [`neighbor()`](functions-neighbor.html "neighbor\(\)"), or [`partition()`](functions-partition.html "partition\(\)"). 

### Related Functions

LogScale offers several related functions for handling sequential events that do not have the same restrictions as sequence functions. Related functions are, for example, [`window()`](functions-window.html "window\(\)"), [`series()`](functions-series.html "series\(\)"), [`session()`](functions-session.html "session\(\)"). 

For more information about the restrictions for sequence functions, see [Using Sequence Query Functions](functions-sequence.html#functions-sequence-restrictions "Using Sequence Query Functions").
