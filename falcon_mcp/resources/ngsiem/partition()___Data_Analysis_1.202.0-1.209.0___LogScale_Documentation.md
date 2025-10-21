# partition() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-partition.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`partition()`](functions-partition.html "partition\(\)")

The [`partition()`](functions-partition.html "partition\(\)") function splits a sequence of events into multiple partitions (subsequences) based on a condition. It allows you to apply a sub-aggregation to each partition separately, useful for grouping related events and performing calculations within these groups, while keeping the order. 

For more information about sequence functions and combined usage, see [Sequence Query Functions](functions-sequence.html "Sequence Query Functions"). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`condition`_](functions-partition.html#query-functions-partition-condition)|  non-aggregate pipeline| required |  |  The condition that determines when to split the sequence into new partitions. The condition is provided as a non-aggregate subquery.   
[_`function`_](functions-partition.html#query-functions-partition-function)[a]| array of aggregate functions| required |  |  The aggregator function(s) to apply to each partition.   
[_`split`_](functions-partition.html#query-functions-partition-split)|  enum| optional[b] | [`before`](functions-partition.html#query-functions-partition-split-option-before)|  Controls whether the split occurs before or after the event that triggers the condition.   
|  |  | **Values**  
|  |  | [`after`](functions-partition.html#query-functions-partition-split-option-after)| Split occurs after the event  
|  |  | [`before`](functions-partition.html#query-functions-partition-split-option-before)| Split occurs before the event  
[a] The parameter name [_`function`_](functions-partition.html#query-functions-partition-function) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`function`_](functions-partition.html#query-functions-partition-function) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     partition("value",condition="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     partition(function="value",condition="value")
> 
> These examples show basic structure only.

Events can also be separated by group using the [`groupBy()`](functions-groupby.html "groupBy\(\)") function. In that case, the events will be sorted by group, whereas [`partition()`](functions-partition.html "partition\(\)") keeps the order of events and splits the groups when the condition is true. An advantage of using [`partition()`](functions-partition.html "partition\(\)") is that it, generally, has a lower memory footprint than [`groupBy()`](functions-groupby.html "groupBy\(\)"). 

### Note

  * The [`partition()`](functions-partition.html "partition\(\)") function must be used after an aggregator function (for example, [`head()`](functions-head.html "head\(\)"), [`sort()`](functions-sort.html "sort\(\)"), [`bucket()`](functions-bucket.html "bucket\(\)"), [`groupBy()`](functions-groupby.html "groupBy\(\)")` timeChart()`) to ensure event ordering, as the [`partition()`](functions-partition.html "partition\(\)") function requires a specific order to calculate cumulative values correctly. 




### [`partition()`](functions-partition.html "partition\(\)") Examples

Click + next to an example below to get the full details.

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

#### Detect All Occurrences of Event A Before Event B

**Detect all occurrences of event A before event B (brute force attack) using the[`partition()`](functions-partition.html "partition\(\)") function combined with [`groupBy()`](functions-groupby.html "groupBy\(\)") **

##### Query

logscale
    
    
    head()
    | groupBy(
          key,
          function = partition(
              condition=test(status=="success"),
              split="after",
              [
                  { status="failure" | count(as=failures) }, 
                  range(@timestamp, as=timespan), 
                  selectLast(status)
              ]
          )
      )
    | failures >= 3
    | status = "success"

##### Introduction

In this example, the [`partition()`](functions-partition.html "partition\(\)") function is used with the [`groupBy()`](functions-groupby.html "groupBy\(\)") function to detect all occurrences of event A before event B (brute force attack). 

The query will detect instances where there were 3 or more failed attempts followed by a successful attempt within the specified 10-second window. 

Note that the [`partition()`](functions-partition.html "partition\(\)") function must be used after an aggregator function to ensure event ordering. Also note that the events must be sorted in order by timestamp to prevent errors when running the query. It is possible to select any field to use as a timestamp. 

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
               function = partition(
                   condition=test(status=="success"),
                   split="after",
                   [
                       { status="failure" | count(as=failures) }, 
                       range(@timestamp, as=timespan), 
                       selectLast(status)
                   ]
               )
           )

Groups the events by a specified key (for example, a user ID or IP address), filters for successful events (filters for events that meet the defined condition for the field status that must contain the value `success`), then splits the data after each successful event. Notice how the condition is provided as a non-aggregate subquery. 

Furthermore, it filters all the failed attempts where the field status contains the value `failure`. 

Makes a count of all the failed attempts, and returns the results in a field named failures, calculates the timespan of the failures, and selects the status of the last event. Calculating the timespan of the failure sequence, is useful for analysis. 

  4. logscale
         
         | failures >= 3

Filters for partitions with 3 or more failures. 

  5. logscale
         
         | status = "success"

Filters for partitions containing the value `success` in the status field. 

  6. Event Result set.




##### Summary and Results

The query is used to detect all occurrences of potential brute force attack patterns. It looks for instances where there were 3 or more failed attempts (event A) followed by a successful attempt (event B), regardless of the time between failures. The timespan between each attempt is reported, which could be used to identify brute force attacks. 

Sample output from the incoming example data: 

key| failures| timespan| status  
---|---|---|---  
a| 5| 1600| success  
a| 3| 300| success  
c| 3| 3100| success  
  
#### Detect Event A Happening X Times Before Event B

**Detect event A happening X times before event B (brute force attack) using the[`partition()`](functions-partition.html "partition\(\)") function combined with [`groupBy()`](functions-groupby.html "groupBy\(\)") **

##### Query

logscale
    
    
    head()
    | groupBy(
        key,
        function = partition(
            condition=test(status=="success"),
            split="after",
            [
                { status="failure" | count(as=failures) }, 
                range(@timestamp, as=timespan), 
                max(@timestamp), 
                selectLast(status)
            ]
        )
    )
    | failures >= 3
    | status = "success"

##### Introduction

In this example, the [`partition()`](functions-partition.html "partition\(\)") function is used with the [`groupBy()`](functions-groupby.html "groupBy\(\)") function to detect event A happening X times before event B (brute force attack). 

The query will detect instances where there were 3 or more failed attempts followed by a successful attempt within the specified 10-second window. 

Note that the [`partition()`](functions-partition.html "partition\(\)") function must be used after an aggregator function to ensure event ordering. Also note that the events must be sorted in order by timestamp to prevent errors when running the query. It is possible to select any field to use as a timestamp. 

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
1451606304500| a| <no value>  
1451606304600| c| failure  
1451606304700| c| failure  
1451606304800| c| failure  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         head()

Selects the oldest events ordered by time. 

  3. logscale
         
         | groupBy(
             key,
             function = partition(
                 condition=test(status=="success"),
                 split="after",
                 [
                     { status="failure" | count(as=failures) }, 
                     range(@timestamp, as=timespan), 
                     max(@timestamp), 
                     selectLast(status)
                 ]
             )
         )

Groups the events by a specified key (for example, a user ID or IP address), then splits the sequence of events after each successful event (where the condition `status=="success"`). 

For each partition, it counts the number of `failure` in status and stores it in the field failures, finds the range of timestamps in the partition, finds the newest timestamp, and finds the latest status to show if the partition ended with a success. 

  4. logscale
         
         | failures >= 3

Filters for partitions that contained 3 or more failures. 

  5. logscale
         
         | status = "success"

Filters for partitions with the value `success` in the status field to ensure that the final status is a success. 

  6. Event Result set.




##### Summary and Results

The query is used to detect instances where there are 3 or more failed attempts followed by a successful attempt. The query can be used to detect a brute force attack where an attacker tries multiple times before succeeding. Note that the effectiveness of this query depends on the nature of your data and the typical patterns in your system. 

Sample output from the incoming example data: 

key| failures| timespan| status  
---|---|---|---  
a| 5| 1600| success  
a| 3| 300| success  
c| 3| 3100| success  
  
#### Divide Data Into Separate Partitions

**Divide data into separate partitions based on a specific condition using the[`partition()`](functions-partition.html "partition\(\)") function **

##### Query

logscale
    
    
    head()
    | partition(count(), condition=test(splitHere))

##### Introduction

In this example, the [`partition()`](functions-partition.html "partition\(\)") function is used with the [`head()`](functions-head.html "head\(\)") function to count the number of events in each group, starting a new count whenever the field splitHere is `true`. 

Note that the [`partition()`](functions-partition.html "partition\(\)") function must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

splitHere  
---  
false  
false  
false  
true  
false  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         head()

Selects the oldest events ordered by time. 

  3. logscale
         
         | partition(count(), condition=test(splitHere))

Splits the events (creates a new subsequence) whenever the splitHere field is `true` and counts the number of events in each partition (group), returning the results in a field named _count. 

For example, if you have five events and the third one has the field splitHere as `true`, two groups are created: 

     * **Group 1:** 3 events (including the "true" point) 

     * **Group 2:** 2 events 

Note that it is possible to split after the event, where the condition is `true`: 

logscale
    
    partition(count(), condition=test(splitHere), split=after)

. 
  4. Event Result set.




##### Summary and Results

The query is used to split a sequence of events into multiple partitions based on a conditional test. 

Sample output from the incoming example data: 

_count  
---  
3  
2  
  
Sample output from the incoming example data if condition is true and split equals `after`: 

_count  
---  
4  
1  
  
The query is useful for grouping related events and performing calculations within these groups.
