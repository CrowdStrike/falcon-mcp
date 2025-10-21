# neighbor() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-neighbor.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`neighbor()`](functions-neighbor.html "neighbor\(\)")

The [`neighbor()`](functions-neighbor.html "neighbor\(\)") function allows access to fields from a single neighboring event in a sequence. It retrieves fields from either a preceding or succeeding event at a specified distance from the current event. The [`neighbor()`](functions-neighbor.html "neighbor\(\)") function is particularly useful for comparing events or detecting patterns in sequential data. 

For more information about sequence functions and combined usage, see [Sequence Query Functions](functions-sequence.html "Sequence Query Functions"). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`direction`_](functions-neighbor.html#query-functions-neighbor-direction)|  enum| optional[a] | [`preceding`](functions-neighbor.html#query-functions-neighbor-direction-option-preceding)|  Specifies whether to look at preceding or succeeding events.   
|  |  | **Values**  
|  |  | [`preceding`](functions-neighbor.html#query-functions-neighbor-direction-option-preceding)| Look at preceding events  
|  |  | [`succeeding`](functions-neighbor.html#query-functions-neighbor-direction-option-succeeding)| Look at succeeding events  
[ _`distance`_](functions-neighbor.html#query-functions-neighbor-distance)|  integer| optional[[a]](functions-neighbor.html#ftn.table-functions-neighbor-optparamfn) | `1`|  The number of events to look ahead or behind.   
|  | **Maximum**| [`10000`](functions-neighbor.html#query-functions-neighbor-distance-max-10000)| 10,000 events  
[ _`include`_](functions-neighbor.html#query-functions-neighbor-include)[b]| array of strings| required |  |  The fields to include from the neighboring event.   
[_`prefix`_](functions-neighbor.html#query-functions-neighbor-prefix)|  string| optional[[a]](functions-neighbor.html#ftn.table-functions-neighbor-optparamfn) |  |  A prefix to add to the included field names to distinguish them from the current event's fields.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`include`_](functions-neighbor.html#query-functions-neighbor-include) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`include`_](functions-neighbor.html#query-functions-neighbor-include) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     neighbor(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     neighbor(include=["value"])
> 
> These examples show basic structure only.

### Note

  * The [`neighbor()`](functions-neighbor.html "neighbor\(\)") function must be used after an aggregator function (for example, [`head()`](functions-head.html "head\(\)"), [`sort()`](functions-sort.html "sort\(\)"), [`bucket()`](functions-bucket.html "bucket\(\)"), [`groupBy()`](functions-groupby.html "groupBy\(\)")` timeChart()`) to ensure event ordering, as the [`neighbor()`](functions-neighbor.html "neighbor\(\)") function requires a specific order to calculate cumulative values correctly. 

  * The neighbor can be found a maximum of 10,000 events away. 




### [`neighbor()`](functions-neighbor.html "neighbor\(\)") Examples

Click + next to an example below to get the full details.

#### Access Fields From Single Neighboring Event in a Sequence - Example 1

**Access fields from a single neighboring (preceeding) event in a sequence using the[`neighbor()`](functions-neighbor.html "neighbor\(\)") function **

##### Query

logscale
    
    
    head()
    | neighbor(key, prefix=prev)

##### Introduction

In this example, the [`neighbor()`](functions-neighbor.html "neighbor\(\)") function is used to look at the preceeding event; the one just before the current event as no distance is specified. 

Note that the [`neighbor()`](functions-neighbor.html "neighbor\(\)") function must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

key  
---  
a  
a  
b  
c  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         head()

Selects the oldest events ordered by time. 

  3. logscale
         
         | neighbor(key, prefix=prev)

For each event, looks at the event immediately before it, and returns the value of the field key within the current event as a field named prev.key. 

It is also possible to look at an event further away, if defining a distance: `neighbor(key, prefix=prev, distance=2)`

  4. Event Result set.




##### Summary and Results

In this example, the value of a field from a preceding event is added to each event. 

Sample output from the incoming example data: 

key| prev.key  
---|---  
a| <no value>  
a| a  
b| a  
c| b  
  
The query is useful for comparing events or detecting patterns in sequential data. 

#### Access Fields From Single Neighboring Event in a Sequence - Example 2

**Access fields from a single neighboring (succeeding) event in a sequence using the[`neighbor()`](functions-neighbor.html "neighbor\(\)") function **

##### Query

logscale
    
    
    head()
    | neighbor(key, prefix=succ, direction=succeeding)

##### Introduction

In this example, the [`neighbor()`](functions-neighbor.html "neighbor\(\)") function is used to look at the succeeding event; the one just after the current event as no distance is specified. 

Note that the [`neighbor()`](functions-neighbor.html "neighbor\(\)") function must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

key  
---  
a  
a  
b  
c  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         head()

Selects the oldest events ordered by time. 

  3. logscale
         
         | neighbor(key, prefix=succ, direction=succeeding)

For each event, looks at the event immediately after it, and returns the results in a field named succ.key. 

  4. Event Result set.




##### Summary and Results

The query is used to access fields from a single neighboring event in a sequence, retrieving fields from either a preceding or succeeding event at a specified distance (number of events) from the current event. 

Sample output from the incoming example data: 

key| succ.key  
---|---  
a| a  
a| b  
b| c  
c| <no value>  
  
The query is useful for comparing event values or detecting patterns in sequential data. 

#### Access Fields From Single Neighboring Event in a Sequence - Example 3

**Access fields from a single neighboring (further away) event in a sequence using the[`neighbor()`](functions-neighbor.html "neighbor\(\)") function **

##### Query

logscale
    
    
    head()
    | neighbor(key, prefix=prev, distance=2)

##### Introduction

In this example, the [`neighbor()`](functions-neighbor.html "neighbor\(\)") function is used to look at a preceeding event with the specified distance of `2` away from the current event. 

Note that the [`neighbor()`](functions-neighbor.html "neighbor\(\)") function must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

key  
---  
a  
a  
b  
c  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         head()

Selects the oldest events ordered by time. 

  3. logscale
         
         | neighbor(key, prefix=prev, distance=2)

For each event, looks two events back in the sequence. It retrieves the key value from that event two positions back, and adds this value to the current event's data, labeled with prev.key. 

  4. Event Result set.




##### Summary and Results

The query is used to access fields from each event at a specified distance (number of events) away in a sequence of events, retrieving fields from either a preceding or succeeding event at a specified distance from the current event. 

Sample output from the incoming example data: 

key| prev.key  
---|---  
a| <no value>  
a| <no value>  
b| a  
c| a  
  
The query is useful for comparing events with others that are not immediately adjacent in your data sequence. 

#### Count Events Within Partitions Based on Condition

**Count events within partitions based on a specific condition using the[`partition()`](functions-partition.html "partition\(\)") function combined with [`neighbor()`](functions-neighbor.html "neighbor\(\)") and [`accumulate()`](functions-accumulate.html "accumulate\(\)") **

##### Query

logscale
    
    
    head()
    | neighbor(key, prefix=prev)
    | partition(accumulate(count()), condition=test(key != prev.key))

##### Introduction

Accumulations can be partitioned based on a condition, such as a change in value. This is achieved by combining the three functions [`partition()`](functions-partition.html "partition\(\)"), [`neighbor()`](functions-neighbor.html "neighbor\(\)") and [`accumulate()`](functions-accumulate.html "accumulate\(\)"). In this example, the combination of the 3 sequence functions is used to count events within partitions defined by changes in a key field. 

Note that sequence functions must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

key  
---  
a  
a  
a  
b  
a  
b  
b  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         head()

Selects the oldest events ordered by time. 

  3. logscale
         
         | neighbor(key, prefix=prev)

Accesses the value in the field key from the previous event. 

  4. logscale
         
         | partition(accumulate(count()), condition=test(key != prev.key))

The [`partition()`](functions-partition.html "partition\(\)") function splits the sequence of events based on the specified condition. A new partition starts when the current key value is different from the previous key value. Within each partition, it counts the number of events, and returns the results in a field named _count. 

  5. Event Result set.




##### Summary and Results

The query is used to compute an accumulated count of events within partitions based on a specific condition, in this example change in value for the field key. 

Sample output from the incoming example data: 

key| _count| prev.key  
---|---|---  
a| 1| <no value>  
a| 2| a  
a| 3| a  
b| 1| a  
a| 1| b  
b| 1| a  
b| 2| b  
  
The query is useful for analyzing sequences of events, especially when you want to identify and count consecutive occurrences of a particular attribute in order to identify and analyze patterns or sequences within your data. 

#### Detect Changes And Compute Differences Between Events - Example 1

**Detect changes and compute differences between events using the[`neighbor()`](functions-neighbor.html "neighbor\(\)") function **

##### Query

logscale
    
    
    head()
    | neighbor(value, prefix=prev)
    | change := value - prev.value
    | change > 5

##### Introduction

In this example, the [`neighbor()`](functions-neighbor.html "neighbor\(\)") function is used to detect changes in values and alert on large increase. 

Note that the [`neighbor()`](functions-neighbor.html "neighbor\(\)") function must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

value  
---  
3  
5.5  
4  
10  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         head()

Selects the oldest events ordered by time. 

  3. logscale
         
         | neighbor(value, prefix=prev)

Retrieves the value from preceeding event, and assigns this value to the current event's data in a new field named prev.value. 

  4. logscale
         
         | change := value - prev.value

Calculates the difference between current and previous values, and returns the results - the calculated difference - in a field named change. 

  5. logscale
         
         | change > 5

Filters for values in the field change to show only events where the change is greater than `5`. 

  6. Event Result set.




##### Summary and Results

The query is used to detect changes in values and alert on a quantified increase. The query will identify events where the value has increased by more than 5 compared to the previous event. 

Sample output from the incoming example data: 

value| change| prev.value  
---|---|---  
10| 6| 4  
  
The query is useful for real-time monitoring and alerting systems where you need to quickly identify significant changes in sequential data. It allows for immediate detection of anomalies or important shifts in your data, enabling prompt responses to potential issues or opportunities. 

#### Detect Changes And Compute Differences Between Events - Example 2

**Detect changes and compute differences between events using the[`neighbor()`](functions-neighbor.html "neighbor\(\)") function combined with [`accumulate()`](functions-accumulate.html "accumulate\(\)") **

##### Query

logscale
    
    
    head()
    | neighbor(start, prefix=prev)
    | duration := start - prev.start
    | accumulate(sum(duration, as=accumulated_duration))

##### Introduction

In this example, the [`neighbor()`](functions-neighbor.html "neighbor\(\)") function is used with [`accumulate()`](functions-accumulate.html "accumulate\(\)") to calculate a running total of durations. 

Note that the [`neighbor()`](functions-neighbor.html "neighbor\(\)") function must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

start  
---  
1100  
1233  
3002  
4324  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         head()

Selects the oldest events ordered by time. 

  3. logscale
         
         | neighbor(start, prefix=prev)

Retrieves the value in the start field from preceeding event, and assigns this value to the current event's data in a new field named prev.start. 

  4. logscale
         
         | duration := start - prev.start

Calculates the time difference between current and previous start values, and returns the results - the calculated difference - in a field named duration. 

  5. logscale
         
         | accumulate(sum(duration, as=accumulated_duration))

Calculates a running total sum of the values in the field duration and returns the results in a field named accumulated_duration. Each event will show its individual duration and the total accumulated duration up to that point. 

  6. Event Result set.




##### Summary and Results

The query is used to calculate the time difference between consecutive events. The format of this query is a useful pattern when analyzing temporal data, to provide insights into process efficiency, system performance over time etc. In this example, the acculated_duration provides a value that can be used to compare against the duration field within each event. 

Sample output from the incoming example data: 

start| accumulated_duration| duration| prev.start  
---|---|---|---  
1100| 0| <no value>| <no value>  
1233| 133| 133| 1100  
3002| 1902| 1769| 1233  
4324| 3224| 1322| 3002  
  
For example, in the results, the third event shows a large increase in duration against the accumulated_duration and the start time of the previous event (in prev.start). If analyzing execution times of a process, this could indicate a fault or delay compared to previous executions. 

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
  
#### Find Overlapping User Sessions

**Detect when user sessions overlap in time using the[`neighbor()`](functions-neighbor.html "neighbor\(\)") function within [`groupBy()`](functions-groupby.html "groupBy\(\)") **

##### Query

logscale
    
    
    groupBy(user.id, function=neighbor(include=[startTime, endTime], prefix=previous))
    | groupBy(user.id, function=neighbor(direction=succeeding, include=[startTime, endTime], prefix=next))
    | case {
            test(startTime <= previous.endTime) | overlaps := "previous";
            test(endTime >= next.startTime) | overlaps := "next";
            }
    | select([user.id, startTime, endTime, overlaps, previous.startTime, previous.endTime, next.startTime, next.endTime])

##### Introduction

In this example, the [`neighbor()`](functions-neighbor.html "neighbor\(\)") function is used to identify overlapping user sessions by comparing session start and end times with both previous and next sessions for each user. The function is implemented as part of [`groupBy()`](functions-groupby.html "groupBy\(\)") operations for optimal performance, as this approach processes the data in a single pass. 

Example incoming data might look like this: 

@timestamp| user.id| startTime| endTime  
---|---|---|---  
2025-08-06T10:00:00Z| user1| 2025-08-06T10:00:00Z| 2025-08-06T10:30:00Z  
2025-08-06T10:15:00Z| user1| 2025-08-06T10:15:00Z| 2025-08-06T10:45:00Z  
2025-08-06T10:45:00Z| user1| 2025-08-06T10:45:00Z| 2025-08-06T11:15:00Z  
2025-08-06T10:00:00Z| user2| 2025-08-06T10:00:00Z| 2025-08-06T10:20:00Z  
2025-08-06T10:30:00Z| user2| 2025-08-06T10:30:00Z| 2025-08-06T10:50:00Z  
2025-08-06T11:00:00Z| user2| 2025-08-06T11:00:00Z| 2025-08-06T11:20:00Z  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(user.id, function=neighbor(include=[startTime, endTime], prefix=previous))

Groups events by user.id and uses [`neighbor()`](functions-neighbor.html "neighbor\(\)") to access the previous session's startTime and endTime. The [_`prefix`_](functions-neighbor.html#query-functions-neighbor-prefix) parameter adds `previous.` to the field names in the output. Using [`neighbor()`](functions-neighbor.html "neighbor\(\)") as part of the [`groupBy()`](functions-groupby.html "groupBy\(\)") function is significantly more efficient than using it separately, as it allows the operation to be performed during group creation, eliminating the need for additional filtering and transformation steps to manually find sessions for particular users. 

  3. logscale
         
         | groupBy(user.id, function=neighbor(direction=succeeding, include=[startTime, endTime], prefix=next))

Groups events by user.id again and uses [`neighbor()`](functions-neighbor.html "neighbor\(\)") to access the next session's startTime and endTime. The [_`direction`_](functions-neighbor.html#query-functions-neighbor-direction) parameter is set to `succeeding` to look at the next event, and the prefix adds `next.` to the field names. This second grouping operation maintains the performance benefits of integrating [`neighbor()`](functions-neighbor.html "neighbor\(\)") within [`groupBy()`](functions-groupby.html "groupBy\(\)"). 

  4. logscale
         
         | case {
                 test(startTime <= previous.endTime) | overlaps := "previous";
                 test(endTime >= next.startTime) | overlaps := "next";
                 }

Uses a case statement to evaluate two conditions and returns the results in a new field named overlaps. The field indicates whether a session overlaps with either its previous or next session: 

     * First test: ` test(startTime <= previous.endTime) ` checks if the current session starts before or at the same time as when the previous session ends. If true, it assigns `previous` to the overlaps field. 

     * Second test: ` test(endTime >= next.startTime) ` checks if the current session ends after or at the same time as when the next session starts. If true, it assigns `next` to the overlaps field. 

Note that if a session has no overlaps, the overlaps field will not be created for that event. 

  5. logscale
         
         | select([user.id, startTime, endTime, overlaps, previous.startTime, previous.endTime, next.startTime, next.endTime])

Explicitly selects and orders the output fields for clarity. This ensures consistent output formatting and removes any additional fields that might have been created during the processing steps. 

  6. Event Result set.




##### Summary and Results

The query is used to identify user sessions that overlap in time with either their previous or next sessions. 

This query is useful, for example, to detect potential security issues where a user appears to be logged in from multiple locations simultaneously, or to identify problems with session management in applications. 

### Note

Note that this query is optimized for performance by incorporating the [`neighbor()`](functions-neighbor.html "neighbor\(\)") function within the [`groupBy()`](functions-groupby.html "groupBy\(\)") operations. This approach is significantly more efficient than applying [`neighbor()`](functions-neighbor.html "neighbor\(\)") separately after grouping, as it reduces the number of processed events by the [`neighbor()`](functions-neighbor.html "neighbor\(\)") function and leverages LogScale's internal optimizations for grouped operations. 

Sample output from the incoming example data: 

user.id| startTime| endTime| overlaps| previous.startTime| previous.endTime| next.startTime| next.endTime  
---|---|---|---|---|---|---|---  
user1| 2025-08-06T10:00:00Z| 2025-08-06T10:30:00Z| next| <no value>| <no value>| 2025-08-06T10:15:00Z| 2025-08-06T10:45:00Z  
user1| 2025-08-06T10:15:00Z| 2025-08-06T10:45:00Z| previous| 2025-08-06T10:00:00Z| 2025-08-06T10:30:00Z| 2025-08-06T10:45:00Z| 2025-08-06T11:15:00Z  
user1| 2025-08-06T10:45:00Z| 2025-08-06T11:15:00Z| previous| 2025-08-06T10:15:00Z| 2025-08-06T10:45:00Z| <no value>| <no value>  
  
The output demonstrates the overlap detection: sessions are marked as overlapping with either their previous session or their next session. The overlaps field contains either `previous` or `next` depending on which neighboring session overlaps with the current session. 

The results from this query would be well-suited for visualization in a time chart widget, showing the overlapping sessions across time.
