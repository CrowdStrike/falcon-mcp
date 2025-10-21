# groupBy() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-groupby.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:May 21, 2025

## [`groupBy()`](functions-groupby.html "groupBy\(\)")

The [`groupBy()`](functions-groupby.html "groupBy\(\)") query function is used to group together events by one or more specified fields. This is similar to the `GROUP BY` method in SQL databases. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`field`_](functions-groupby.html#query-functions-groupby-field)[a]| array of strings| required |  |  This specifies which field or fields to group.   
[_`function`_](functions-groupby.html#query-functions-groupby-function)|  array of aggregate functions| optional[b] | `count(as=_count)`|  This specifies which aggregate functions to use with each group. If several aggregators are listed for the [_`function`_](functions-bucket.html#query-functions-bucket-function) parameter, then their outputs are combined using the rules described for [`stats()`](functions-stats.html "stats\(\)").   
[_`limit`_](functions-groupby.html#query-functions-groupby-limit)|  string| optional[[b]](functions-groupby.html#ftn.table-functions-groupby-optparamfn) | `20,000`|  This sets the limit for the number of group elements. Default value controlled by [`GroupDefaultLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-group_default_limit.html) dynamic configuration, max value controlled by [`GroupMaxLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-group_max_limit.html). If the argument is `max` (`limit=max`), then the value of [`GroupMaxLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-group_max_limit.html) is used. It prioritizes the top-N series. The top N value being the series with the highest numerical value attributed to it by the subquery across all fields.   
|  |  | **Values**  
|  |  | [`max`](functions-groupby.html#query-functions-groupby-limit-option-max)| The value of [`GroupMaxLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-group_max_limit.html)  
|  | **Maximum**| `1,000,000`|   
|  | **Controlling Variables**  
|  | [`GroupMaxLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-group_max_limit.html)|  **Variable default:**`1,000,000 group elements`  
[a] The parameter name [_`field`_](functions-groupby.html#query-functions-groupby-field) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-groupby.html#query-functions-groupby-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     groupBy([a,b])
> 
> and:
> 
> logscale Syntax
>     
>     
>     groupBy(field=[a,b])
> 
> These examples show basic structure only.

### [`groupBy()`](functions-groupby.html "groupBy\(\)") Function Operation

The [`groupBy()`](functions-groupby.html "groupBy\(\)") function has specific implementation and operational considerations, outlined below. 

  * When [`groupBy()`](functions-groupby.html "groupBy\(\)") reaches its limit, each group may not have processed all relevant events. Consequently, when using count as the subaggregate function,[`groupBy()`](functions-groupby.html "groupBy\(\)") will produce a lower bound estimate. 




#### Series Selection in [`groupBy()`](functions-groupby.html "groupBy\(\)")

The selection is based on the aggregate numerical output across all specified functions and all time buckets, not the series identifiers themselves. 

The [_`limit`_](functions-groupby.html#query-functions-groupby-limit) prioritizes the top-N series. The top N value being the series with the highest numerical value attributed to it by the subquery across all fields. 

Series Selection Process: 

  * The selection is based on the numerical values produced by the subquery/function. 

  * It is not based on the series names. 

  * When multiple functions are used, the function considers all values produced. 




For different examples of top N series selection, see [Find Top N Value of Series - Example 1](https://library.humio.com/examples/examples-timechart-topnvalue-single-function.html) and [Find Top N Value of Series - Example 2](https://library.humio.com/examples/examples-timechart-topnvalue-multi-functions.html). 

#### Grouping in [`groupBy()`](functions-groupby.html "groupBy\(\)")

The [`groupBy()`](functions-groupby.html "groupBy\(\)") can be used to execute aggregate functions on each group. The fields generated are grouped by the field or fields in the [_`field`_](functions-groupby.html#query-functions-groupby-field) parameter for each aggregate function. For example, by default the [`count()`](functions-count.html "count\(\)") function is used and the grouped count returned in the _count field by default. 

The default is to use [`count()`](functions-count.html "count\(\)") as an aggregate function. However, if the goal is to only find the unique values of a field or combinations of multiple fields, then [`groupBy()`](functions-groupby.html "groupBy\(\)") can be provided with an empty list as its aggregate function. 

When showing time series data, the [`timeChart()`](functions-timechart.html "timeChart\(\)") and [`bucket()`](functions-bucket.html "bucket\(\)") functions are an extension of [`groupBy()`](functions-groupby.html "groupBy\(\)") that groups by time. 

#### Limits when using [`groupBy()`](functions-groupby.html "groupBy\(\)")

### Warning

The [`groupBy()`](functions-groupby.html "groupBy\(\)") may return incomplete results limited to a restricted subset of groups and related events, in cases where the [_`limit`_](functions-groupby.html#query-functions-groupby-limit) parameter is exceeded. 

The [`groupBy()`](functions-groupby.html "groupBy\(\)") function is limited in the number of groups it will handle. Such limit is set in the LogScale configuration using GraphQL mutations bound by the [`GroupMaxLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-group_max_limit.html) dynamic configuration. 

Starting from version 1.127, the maximum value of the [_`limit`_](functions-groupby.html#query-functions-groupby-limit) parameter is 1,000,000 by default (adjustable by the corresponding [`GroupMaxLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-group_max_limit.html) dynamic configuration), which means it is possible to create up to 1 Million groups. 

When the [_`limit`_](functions-groupby.html#query-functions-groupby-limit) parameter is not supplied explicitly, its default value is determined by the [`GroupDefaultLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-group_default_limit.html) dynamic configuration, which has a default value of 20,000. 

[`GroupDefaultLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-group_default_limit.html) cannot be higher than [`GroupMaxLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-group_max_limit.html). 

Attention

The _`limit`_ parameter is governed by the dynamic configurations [`GroupMaxLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-group_max_limit.html) and [`GroupDefaultLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-group_default_limit.html) to the same value for a seamless upgrade. 

Additionally, like all LogScale functions, [`groupBy()`](functions-groupby.html "groupBy\(\)") has an internal memory limit determined by the dynamic configuration [`QueryCoordinatorMemoryLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-query_coordinator_memory_limit.html). This means that it is possible for the function to collect less than the specified limit number of groups, if the total amount of data collected by the function exceeds this limit. The internal memory limit is in place to protect the cluster health, and ensure sufficient memory for other queries to run. Should the memory limit be reached, no more groups are added. This may lead to results that are inconsistent with the results shown prior to the limit being reached. The groups that were present in prior results may be pushed out of the result set during merges between nodes, to ensure that the memory usage is kept within bounds. If a group is shown, the results for that group will be correct. In situations where you reach the memory limit, you may want to use the [`top()`](functions-top.html "top\(\)") function to narrow the list of groups. 

One of the reasons for this limitation is because [`groupBy()`](functions-groupby.html "groupBy\(\)") is implemented to work entirely in memory, and cannot spill to disk. The limit helps to prevent searches from consuming too much memory. This method and limitation may be changed in future versions of LogScale. 

### [`groupBy()`](functions-groupby.html "groupBy\(\)") Syntax Examples

Since the most common use-case is to count the distinct values of a field, the default behavior is to use [`count()`](functions-count.html "count\(\)") to aggregate the events. The simplest use-case of [`groupBy()`](functions-groupby.html "groupBy\(\)") is, therefore, to count the occurrence of the distinct values of a field: 

logscale
    
    
    groupBy(status_code)

Given input: 

status_code |  ip   
---|---  
440 |  1.111.111.111   
500 |  1.111.111.111   
440 |  1.111.111.111   
440 |  2.222.222.222   
  
The output is: 

status_code |  _count   
---|---  
440 |  3   
500 |  1   
  
The task is to only find the unique values, [`groupBy()`](functions-groupby.html "groupBy\(\)") can be provided with an empty list as the aggregate function, implying that nothing will be aggregated: 

logscale
    
    
    groupBy(status_code, function=[])

The output is: 

status_code   
---  
440   
500   
  
Similarly, [`groupBy()`](functions-groupby.html "groupBy\(\)") can be used to find the unique combinations of field values present in the data: 

logscale
    
    
    groupBy([status_code, ip], function=[])

The output is: 

status_code |  ip   
---|---  
440 |  1.111.111.111   
500 |  1.111.111.111   
440 |  2.222.222.222   
  
A usage of the function such as the one above is also very useful for query-based parameters in dashboards, see [Query Parameter](dashboards-interactive-parameters.html#dashboards-parameters-type-param2) for more explanations. 

As an example of how to use this query function, suppose you have a LogScale repository that is ingesting data from one or more web servers. Now suppose you want to get a list of HTTP status codes, the results of users accessing the server. For instance, HTTP code 404 for `Not Found` — for web pages not found. You could get a list of all of the HTTP codes returned and a count of each by executing a query that counts the different http status codes, like this: 

logscale
    
    
    groupBy(field=status_code, function=count())
    | sort(statuscode, order=asc)

In addition to the [`groupBy()`](functions-groupby.html "groupBy\(\)"), the results here are piped to the [`sort()`](functions-sort.html "sort\(\)") function to sort the results from the lowest HTTP code to the highest. 

statuscode| _count  
---|---  
200| 7485  
301| 2314  
304| 65  
400| 101  
404| 6425  
405| 2  
408| 9  
  
With the [`groupBy()`](functions-groupby.html "groupBy\(\)") function, you can have LogScale group by more than one field. You would just give the fields in an array, a comma-separated list within square-brackets. It would look something like this query in which events are grouped on HTTP method and status code: 

logscale
    
    
    groupBy(field=[method, statuscode], function=count())
    | sort([method, statuscode], order=asc)

Will produce these results: 

method| statuscode  
---|---  
CONNECT| 301  
GET| 200  
GET| 301  
GET| 304  
GET| 400  
GET| 404  
HEAD| 200  
HEAD| 301  
HEAD| 400  
HEAD| 404  
OPTIONS| 200  
OPTIONS| 301  
POST| 200  
POST| 301  
POST| 400  
POST| 404  
  
Although this query works, you may also want to show the total for each method, not just the total for each status code of each method. To do that, you'll have to adjust the query to look like this: 

logscale
    
    
    [groupBy(method, function=[count(as=method_total), groupBy(statuscode, function=count(as=method_status_count))])]

In this query, a [`groupBy()`](functions-groupby.html "groupBy\(\)") is nested within another [`groupBy()`](functions-groupby.html "groupBy\(\)"). The results will look like this: 

method| method_total| statuscode| method_status_count  
---|---|---|---  
GET| 14078| 200| 7326  
GET| 14078| 301| 1246  
GET| 14078| 304| 65  
GET| 14078| 400| 70  
GET| 14078| 404| 5371  
HEAD| 139| 200| 14  
HEAD| 139| 301| 22  
HEAD| 139| 400| 6  
HEAD| 139| 404| 97  
POST| 2005| 200| 14  
POST| 2005| 301| 1002  
POST| 2005| 400| 25  
POST| 2055| 404| 964  
  
These results still might not be as tidy as you like. You might do better with separate queries for each method or each status code — assuming you're interested in only a few specific ones. Another possibility might be to use an [API](https://library.humio.com/logscale-api/api.html) to be able to assemble the results in a manner that you prefer. 

Instead of a single function, additional query functions can be also applied, allowing for calculations on the count that is obtained from [`groupBy()`](functions-groupby.html "groupBy\(\)"). The following query contains an embedded expression within [`groupBy()`](functions-groupby.html "groupBy\(\)"), as a demonstration of formatting/calculating the value within a [`groupBy()`](functions-groupby.html "groupBy\(\)") expression: 

logscale
    
    
    groupBy(host, function=[{count()
    | esp:=_count/300}])

The query generates a [`count()`](functions-count.html "count\(\)") of the number of hosts in the aggregation, which creates a field _count which is then divided by `300` and placed into the field esp. 

### [`groupBy()`](functions-groupby.html "groupBy\(\)") Examples

Click + next to an example below to get the full details.

#### Sort Timestamps With [`groupBy()`](functions-groupby.html "groupBy\(\)")

**Sorting fields based on aggregated field values**

##### Query

**Search Repository:** [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html)

logscale
    
    
    timestamp := formatTime(format="%H:%M")
    | groupBy([thread],
    function=[{sort("timestamp")
    | collect("timestamp")}])

##### Introduction

When using aggregation, you may want to sort on a field that is part of the aggregated set but not the main feature of the aggregated value. For example, sorting the values by their timestamp rather than the embedded value. To achieve this, you should use a function that sorts the field to be used as the sort field, and then use [`collect()`](functions-collect.html "collect\(\)") so that the value from before the aggregation can be displayed in the generated event set. This query can be executed in the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) respository. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         timestamp := formatTime(format="%H:%M")

Creates a new field, timestamp formatted as `HH:MM`. 

  3. logscale
         
         | groupBy([thread],

Groups the events, first by the name of the thread and then the formatted timestamp. 

  4. logscale
         
         function=[{sort("timestamp")
         | collect("timestamp")}])

Uses the [`sort()`](functions-sort.html "sort\(\)") combined with [`collect()`](functions-collect.html "collect\(\)") as the method fo aggregation. As an embedded expression for the function, this will sort the events on the timestamp field and then retrieve the field as it would normally be removed as part of the aggregation process. 

  5. Event Result set.




##### Summary and Results

The result set will contain a list of the aggregated thread names sorted by the timestamp: 

thread| timestamp  
---|---  
BootstrapInfoJob| 10:09  
DataSynchJob| 10:09  
Global event loop| 10:10  
LocalLivequeryMonitor| 10:09  
LogCollectorManifestUpdate| 10:09  
TransientChatter event loop| 10:10  
aggregate-alert-job| 10:09  
alert-job| 10:09  
block-processing-monitor-job| 10:09  
bloom-scheduler| 10:09  
bucket-entity-config| 10:09  
bucket-overcommit-metrics-job| 10:09  
bucket-storage-download| 10:09  
bucket-storage-prefetch| 10:09  
chatter-runningqueries-logger| 10:09  
chatter-runningqueries-stats| 10:09  
  
#### Deduplicate Content by Field

**Deduplicating content based on a specific field**

##### Query

logscale
    
    
    groupBy(field, function=tail(1))

##### Introduction

If you want to deduplicate events by a given field, for example to identify a unique list of events for further processing, you can use an aggregate function. In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") function is used with [`tail()`](functions-tail.html "tail\(\)") to use the last value in a sequence of events. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(field, function=tail(1))

Groups all events in a specific field, and reduces the results using [`tail()`](functions-tail.html "tail\(\)") to take only the last value. 

  3. Event Result set.




##### Summary and Results

The query is used to deduplicate events by a given field. This is useful if you want to create a unique list of events for further processing. 

#### Aggregate Array Content

****

##### Query

logscale
    
    
    array:contains("incidents[]", value="Cozy Bear")
    | groupBy(host)

##### Introduction

Given events containing an `incidents` array: 

Event 1 
    
    
    |--------------|-------------|
    | host         | v1          |
    | incidents[0] | Evil Bear   |
    | incidents[1] | Cozy Bear   |
    |--------------|-------------|

Event 2 
    
    
    |--------------|-------------|
    | host         | v15         |
    | incidents[0] | Fancy Fly   |
    | incidents[1] | Tiny Cat    |
    | incidents[2] | Cozy Bears  |
    |--------------|-------------|

Finds all the events where the field incidents contains the exact value `Cozy Bear` and group them by which hosts were affected, giving output event: 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:contains("incidents[]", value="Cozy Bear")

Extracts elements from the array incidents from the field host that match the text `Cozy Bear`. The items will be output into the host field. 

  3. logscale
         
         | groupBy(host)

Groups the result events extracted from the array by the host. 

  4. Event Result set.




##### Summary and Results

The result is an aggregated count of the array elements matching `Cozy Bear`. 

field| value  
---|---  
host| v1  
_count| 1  
  
#### Alert Query for Parsers Issues

**Reporting errors**

##### Query

logscale
    
    
    #type=humio #kind=logs
    | loglevel=WARN
    | class = c.h.d.ParserLimitingJob
    | "Setting reject ingest for"
    | groupBy(id, function=[count(), min(@timestamp), max(@timestamp)] )
    | timeDiff:=_max-_min
    | timeDiff > 300000 and _count > 10

##### Introduction

This alert query tries to balance reacting when there are problems with parsers, without being too restrictive. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #type=humio #kind=logs

Filters on all logs across all hosts in the cluster. 

  3. logscale
         
         | loglevel=WARN

Filters for all events where the loglevel is equal to `WARN`. 

  4. logscale
         
         | class = c.h.d.ParserLimitingJob

Assigns the value `c.h.d.ParserLimitingJob` to the class for the logs having the loglevel value `WARN`. 

  5. logscale
         
         | "Setting reject ingest for"

Filters for events containing the string `Setting reject ingest for`. This is the error message generated when ingested events are rejected. 

  6. logscale
         
         | groupBy(id, function=[count(), min(@timestamp), max(@timestamp)] )

Groups the returned result by the field id, makes a count on the events and returns the minimum timestamp and maximum timestamp. This returns a new event set, with the fields id, _count, _min, and _max. 

  7. logscale
         
         | timeDiff:=_max-_min

Calculates the time difference between the maximum timestamp values and the minimum timestamp values and returns the result in a new field named timeDiff. 

  8. logscale
         
         | timeDiff > 300000 and _count > 10

Returns all events where the values of timeDiff is greater that `300000` and where there are more than `10` occurrences. 

  9. Event Result set.




##### Summary and Results

This query is used to set up alerts for parsers issues. Setting up alerts for parsers issues will allow to proactively reach out to customers where their queries are being throttled and help them. 

#### Analyze User Sessions Based on Click Activity

**Analyzes user sessions based on users click activity using the[`session()`](functions-session.html "session\(\)") function **

##### Query

logscale
    
    
    groupBy(cookie_id, function=session(maxpause=15m, count(as=clicks)))
    | sort(clicks)

##### Introduction

In this example, the [`session()`](functions-session.html "session\(\)") function is used to analyze user sessions based on users click activity. The [`session()`](functions-session.html "session\(\)") function groups events by a given timespan. 

Example incoming data might look like this: 

timestamp| cookie_id| action_type| page_url| user_agent  
---|---|---|---|---  
2025-05-15 05:30:00| user123| pageview| /home| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:30:15| user123| click| /products| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:30:30| user123| click| /product/item1| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:31:00| user123| click| /cart| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:31:30| user123| click| /checkout| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:35:00| user456| pageview| /home| Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  
2025-05-15 05:35:30| user456| click| /about| Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  
2025-05-15 05:36:00| user456| click| /contact| Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  
2025-05-15 05:38:00| user789| pageview| /home| Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)  
2025-05-15 05:38:30| user789| click| /products| Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(cookie_id, function=session(maxpause=15m, count(as=clicks)))

Groups events by the field cookie_id (unique user identifier) and creates sessions with 15-minute inactivity timeout (the default value of the [_`maxpause`_](functions-session.html#query-functions-session-maxpause) parameter), then makes a count of each event in a session returning the result in a new field named clicks. 

  3. logscale
         
         | sort(clicks)

Sorts the results by number of clicks (default is descending order). 

  4. Event Result set.




##### Summary and Results

The query is used to analyze user sessions based on the users click activity. The query is useful, for example, to identify most/least active user sessions, detect potential automated behavior or just to understand user engagement levels. 

Sample output from the incoming example data: 

cookie_id| clicks  
---|---  
user123| 5  
user456| 3  
user789| 2  
  
Note that each row represents an event (either pageview or click). 

#### Calculate Events per Second by Host

**Determine event rate for each host over a 5-minute period using an embedded expression within the` groupBy()` function **

##### Query

logscale
    
    
    groupBy(host, function=[{count() | esp:=_count/300}])

##### Introduction

In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") function is used with an embedded expression to calculate the total event count and events per second for each host over a 5-minute period. 

Example incoming data might look like this: 

@timestamp| host| service| status| response_time  
---|---|---|---|---  
2025-08-06T10:00:00Z| server1| web| ok| 120  
2025-08-06T10:00:01Z| server2| database| ok| 85  
2025-08-06T10:00:02Z| server1| web| ok| 95  
2025-08-06T10:00:03Z| server3| cache| ok| 45  
2025-08-06T10:00:04Z| server2| database| error| 250  
2025-08-06T10:00:05Z| server1| web| ok| 110  
2025-08-06T10:00:06Z| server3| cache| ok| 40  
2025-08-06T10:00:07Z| server2| database| ok| 90  
2025-08-06T10:00:08Z| server1| web| error| 300  
2025-08-06T10:00:09Z| server3| cache| ok| 42  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(host, function=[{count() | esp:=_count/300}])

Groups events by the host field and uses an embedded expression to count the number of events per host and calculate events per second in one operation. 

The [`count()`](functions-count.html "count\(\)") function returns the count in a field named _count by default. The embedded expression then divides this value by `300` and stores the result in a new field named esp. This calculation provides the average events per second for each host over the time period. 

Using an embedded expression within the [`groupBy()`](functions-groupby.html "groupBy\(\)") function performs both the count and the calculation as part of the same aggregation. Both the original _count and the calculated esp field are included in the results. 

  3. Event Result set.




##### Summary and Results

The query is used to analyze event frequency patterns by calculating both the total event count and the average events per second for each host. 

Note that the query aggregates against both the original count and the count/300 as one aggregate set. Using an embedded expression is more efficient for larger event sets. 

This query is useful, for example, to monitor system load distribution across hosts, identify hosts with unusual event rates, or establish baseline activity patterns for capacity planning. 

Sample output from the incoming example data: 

host| _count| esp  
---|---|---  
server1| 4| 0.013333  
server2| 3| 0.010000  
server3| 3| 0.010000  
  
Note that the _count field shows the total number of events per host, and the esp field shows the calculated events per second (total events divided by 300 seconds) 

This data is ideal for visualization using a Time Chart widget to show event rates over time. A Bar Chart widget could compare event rates across hosts, while a Gauge widget could show current event rates against predefined thresholds. Consider creating a dashboard that combines these visualizations with alerts for when event rates exceed normal ranges. 

#### Calculate Query Cost for All Users by Repository

**Search across multiple repositories to calculate query costs for all users by repository using[`sort()`](functions-sort.html "sort\(\)") and [`groupBy()`](functions-groupby.html "groupBy\(\)") functions **

##### Query

logscale
    
    
    #type=humio #kind=logs class=c.h.j.RunningQueriesLoggerJob message="Highest Cost query"
     | groupBy(repo, initiatingUser, totalLiveCost, totalStaticCost)
     | sort([totalLiveCost, totalStaticCost])

##### Introduction

In this example, the query uses [`sort()`](functions-sort.html "sort\(\)") and [`groupBy()`](functions-groupby.html "groupBy\(\)") functions to find query costs. The query filters logs in [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository that are tagged with `kind` equal to `logs` and then returns the events where the class field has values containing `c.h.j.RunningQueriesLoggerJob`, searching for the specific value `Highest Cost query`. 

Example incoming data might look like this: 

#type| #kind| class| message| timestamp| dataspace| initiatingUser| totalLiveCost| totalStaticCost| deltaTotalCost| repo  
---|---|---|---|---|---|---|---|---|---|---  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:30:00Z| production| john.doe| 1500| 800| 2300| security-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:31:00Z| development| jane.smith| 2000| 1200| 3200| app-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:32:00Z| staging| bob.wilson| 1000| 500| 1500| infra-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:33:00Z| production| john.doe| 1800| 900| 2700| security-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:34:00Z| development| jane.smith| 2500| 1300| 3800| app-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:35:00Z| staging| alice.cooper| 1200| 600| 1800| infra-logs  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #type=humio #kind=logs class=c.h.j.RunningQueriesLoggerJob message="Highest Cost query"

Filters for Humio internal logs containing `c.h.j. RunningQueriesLoggerJob` in the class field and where the value in the message field is equal to `Highest Cost query`. 

  3. logscale
         
         | groupBy(repo, initiatingUser, totalLiveCost, totalStaticCost)

Groups the results by the repo field, the initiatingUser field, and by both cost types (the fields totalLiveCost, totalStaticCost), and returns a count in a field named _count. 

  4. logscale
         
         | sort([totalLiveCost, totalStaticCost])

Sorts the results by both the totalLiveCost field and the totalStaticCost field, in descending order by default. 

  5. Event Result set.




##### Summary and Results

The query is used to search across multiple repositories and output query costs for all users by repository. The query returns the count in a field named _count. Use this query to focus on live and static costs separately. 

Sample output from the incoming example data: 

repo| initiatingUser| totalLiveCost| totalStaticCost| _count  
---|---|---|---|---  
app-logs| jane.smith| 2000| 1200| 1  
security-logs| john.doe| 1500| 800| 1  
infra-logs| bob.wilson| 1000| 500| 1  
  
#### Calculate Relationship Between X And Y Variables - Example 3 

**Calculate the linear relationship between server load and each of several types of request types using the[`linReg()`](functions-linreg.html "linReg\(\)") function with [`bucket()`](functions-bucket.html "bucket\(\)") and [`groupBy()`](functions-groupby.html "groupBy\(\)") **

##### Query

logscale
    
    
    bucket(function=[ avg(server_load_pct, as=y), groupBy(request_type, function=count(as=x)) ])
    | groupBy(request_type, function=linReg(x=x, y=y))

##### Introduction

In this example, the [`linReg()`](functions-linreg.html "linReg\(\)") function is used to calculate the linear relationship between request_type (`x` variable) and server_load_pct (`y` variable). The example shows the relationship between server load and each of several types of HTTP request types across time. 

Example incoming data might look like this: 

@timestamp| server_load_pct| request_type  
---|---|---  
2024-01-15T09:00:00.000Z| 45.2| GET  
2024-01-15T09:00:00.000Z| 45.2| POST  
2024-01-15T09:00:00.000Z| 45.2| GET  
2024-01-15T09:05:00.000Z| 52.8| GET  
2024-01-15T09:05:00.000Z| 52.8| PUT  
2024-01-15T09:05:00.000Z| 52.8| POST  
2024-01-15T09:10:00.000Z| 48.6| GET  
2024-01-15T09:10:00.000Z| 48.6| GET  
2024-01-15T09:10:00.000Z| 48.6| DELETE  
2024-01-15T09:15:00.000Z| 65.3| POST  
2024-01-15T09:15:00.000Z| 65.3| POST  
2024-01-15T09:15:00.000Z| 65.3| GET  
2024-01-15T09:20:00.000Z| 42.1| GET  
2024-01-15T09:20:00.000Z| 42.1| PUT  
2024-01-15T09:20:00.000Z| 42.1| GET  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bucket(function=[ avg(server_load_pct, as=y), groupBy(request_type, function=count(as=x)) ])

Buckets the data points by time, then calculates the average server load for each time bucket returning the result in a field named y. It also groups the request types in a field named request_type and makes a count of requests by type in each time bucket returning the result in a field named x. 

  3. logscale
         
         | groupBy(request_type, function=linReg(x=x, y=y))

Correlates x with y, showing the relationship between the variables `x` and `y` for each HTTP request type and outputs the results in fields named _slope (slope value),_intercept (intercept value),_r2 (adjusted R-squared value), and _n (number of data points). These four key values indicate relationship strength and reliability. 

  4. Event Result set.




##### Summary and Results

The query is used to analyze how different HTTP request types affect server load. The analysis helps identify which HTTP request types have the strongest impact on server performance. 

Sample output from the incoming example data: 

request_type| _slope| _intercept| _r2| _n  
---|---|---|---|---  
DELETE| <no value>| <no value>| <no value>| <no value>  
GET| -13.749999999999941| 72.7999999999999| 0.5941824574313592| 5  
POST| 16.29999999999992| 32.70000000000012| 0.7196207242484238| 3  
PUT| <no value>| <no value>| <no value>| <no value>  
  
_slope is the impact rate of request volume on server load. 

_intercept is the baseline server load when there are no requests of a specific type. 

_r2 is the statistical accuracy of the relationship. 

_n is the total number of data points analyzed. 

#### Calculate Total Network Bandwidth Per Host

**Analyze network traffic patterns using the[`groupBy()`](functions-groupby.html "groupBy\(\)") function with [`sum()`](functions-sum.html "sum\(\)") **

##### Query

logscale
    
    
    event_simpleName="NetworkConnectStats"
    groupBy([ComputerName], function=[
            sum(field="BytesReceived", as=InboundTraffic),
            sum(field="BytesSent", as=OutboundTraffic)
            ])
    TotalTraffic := InboundTraffic + OutboundTraffic
    sort(field="TotalTraffic", order="desc")

##### Introduction

In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") is used with nested [`sum()`](functions-sum.html "sum\(\)") functions to calculate total inbound and outbound network traffic per host, followed by calculating the total bandwidth consumption. 

Example incoming data might look like this: 

@timestamp| event_simpleName| ComputerName| BytesReceived| BytesSent  
---|---|---|---|---  
1686837825000| NetworkConnectStats| DESKTOP-A1| 15000000| 8500000  
1686837825000| NetworkConnectStats| DESKTOP-A1| 8900000| 4200000  
1686837825000| NetworkConnectStats| LAPTOP-B2| 25000000| 12000000  
1686837826000| NetworkConnectStats| SERVER-C3| 95000000| 45000000  
1686837826000| NetworkConnectStats| DESKTOP-A1| 12000000| 6800000  
1686837826000| NetworkConnectStats| LAPTOP-B2| 18000000| 9500000  
1686837827000| NetworkConnectStats| SERVER-C3| 85000000| 42000000  
1686837827000| NetworkConnectStats| DESKTOP-D4| 5000000| 2800000  
1686837827000| NetworkConnectStats| LAPTOP-B2| 22000000| 11000000  
1686837828000| NetworkConnectStats| SERVER-C3| 105000000| 52000000  
1686837828000| NetworkConnectStats| DESKTOP-D4| 6500000| 3200000  
1686837828000| NetworkConnectStats| DESKTOP-A1| 9800000| 5100000  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         event_simpleName="NetworkConnectStats"

Filters events to include only those where event_simpleName equals `NetworkConnectStats`. 

  3. logscale
         
         groupBy([ComputerName], function=[
                 sum(field="BytesReceived", as=InboundTraffic),
                 sum(field="BytesSent", as=OutboundTraffic)
                 ])

Groups the data by the ComputerName field and calculates two aggregate values: the sum of BytesReceived stored in a field named InboundTraffic, and the sum of BytesSent stored in a field named OutboundTraffic. 

  4. logscale
         
         TotalTraffic := InboundTraffic + OutboundTraffic

Creates a new field named TotalTraffic containing the values from the InboundTraffic and OutboundTraffic fields. 

  5. logscale
         
         sort(field="TotalTraffic", order="desc")

Sorts the results based on the TotalTraffic field in descending order ([_`order`_](functions-sort.html#query-functions-sort-order)=`desc`), showing hosts with highest bandwidth consumption first. 

  6. Event Result set.




##### Summary and Results

The query is used to analyze network bandwidth consumption patterns across different hosts in the network. 

This query is useful, for example, to identify hosts consuming excessive bandwidth, monitor network usage patterns, or detect potential network-intensive applications or anomalies. 

Sample output from the incoming example data: 

ComputerName| InboundTraffic| OutboundTraffic| TotalTraffic  
---|---|---|---  
SERVER-C3| 285000000| 139000000| 424000000  
LAPTOP-B2| 65000000| 32500000| 97500000  
DESKTOP-A1| 45700000| 24600000| 70300000  
DESKTOP-D4| 11500000| 6000000| 17500000  
  
Note that the traffic values are in bytes and that each row represents the aggregated traffic for a unique host 

#### Collect and Group Events by Specified Field - Example 1

**Collect and group events by specified field using[`collect()`](functions-collect.html "collect\(\)") as part of a [`groupBy()`](functions-groupby.html "groupBy\(\)") operation **

##### Query

logscale
    
    
    groupBy(client_ip, function=session(maxpause=1m, collect([url])))

##### Introduction

In this example, the [`collect()`](functions-collect.html "collect\(\)") function is used to collect visitors, each visitor defined as non-active after one minute. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(client_ip, function=session(maxpause=1m, collect([url])))

Collects visitors (URLs), each visitor defined as non-active after one minute and returns the results in an array named client_ip. A count of the events is returned in a _count field. 

  3. Event Result set.




##### Summary and Results

The query is used to collect fields from multiple events into one event. This query analyzes user behavior by grouping events into sessions for each unique client IP address. It then collects all URLs accessed during each session. Collecting should be used on smaller data sets to create a list (or set, or map, or whatever) when you actually need a list object explicitly (for example, in order to pass it on to some other API). This analysis is valuable for understanding user engagement, and identifying potential security issues based on unusual browsing patterns. Using [`collect()`](functions-collect.html "collect\(\)") on larger data set may cause out of memory as it returns the entire data set. 

#### Collect and Group Events by Specified Field - Example 2

**Collect and group events by specified field using[`collect()`](functions-collect.html "collect\(\)") as part of a [`groupBy()`](functions-groupby.html "groupBy\(\)") operation **

##### Query

logscale
    
    
    LocalAddressIP4 = * RemoteAddressIP4 = * aip = *
    | groupBy([LocalAddressIP4, RemoteAddressIP4], function=([count(aip, as=aipCount, distinct=true), collect([aip])]))

##### Introduction

In this example, the [`collect()`](functions-collect.html "collect\(\)") function is used to collect fields from multiple events. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         LocalAddressIP4 = * RemoteAddressIP4 = * aip = *

Filters for all events where the fields LocalAddressIP4, RemoteAddressIP4 and aip are all present. The actual values in these fields do not matter; the query just checks for their existence. 

  3. logscale
         
         | groupBy([LocalAddressIP4, RemoteAddressIP4], function=([count(aip, as=aipCount, distinct=true), collect([aip])]))

Groups the returned results in arrays named LocalAddressIP4 and RemoteAddressIP4, collects all the AIPs (Adaptive Internet Protocol) into an array and performs a count on the field aip. The count of the AIP values is returned in a new field named aipCount. 

  4. Event Result set.




##### Summary and Results

The query is used to collect fields from multiple events into one event. Collecting should be used on smaller data sets to create a list (or set, or map, or whatever) when you actually need a list object explicitly (for example, in order to pass it on to some other API). Using [`collect()`](functions-collect.html "collect\(\)") on larger data set may cause out of memory as it returns the entire data set. The query is useful for network connection analysis and for identifying potential threats. 

Sample output might look like this: 

LocalAddressIP4| RemoteAddressIP4| aipCount| aip  
---|---|---|---  
192.168.1.100| 203.0.113.50| 3| [10.0.0.1, 10.0.0.2, 10.0.0.3]  
10.0.0.5| 198.51.100.75| 1| [172.16.0.1]  
172.16.0.10| 8.8.8.8| 5| [192.0.2.1, 192.0.2.2, 192.0.2.3, 192.0.2.4, 192.0.2.5]  
  
#### Count Unique Visitors Based on Client IP Addresses

**Count unique visitors based on client IP addresses using the[`session()`](functions-session.html "session\(\)") function **

##### Query

logscale
    
    
    groupBy(client_ip, function=session(maxpause=15m))
    | count()

##### Introduction

In this example, the [`session()`](functions-session.html "session\(\)") function is used to count the unique visitors (each visitor defined as non-active for 15 minutes) of a site based on client IP addresses. The [`session()`](functions-session.html "session\(\)") function groups events by a given timespan. 

Example incoming data might look like this: 

timestamp| client_ip| url| status_code| user_agent  
---|---|---|---|---  
2025-05-15 05:30:00| 192.168.1.100| /login| 200| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:31:15| 192.168.1.100| /dashboard| 200| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:32:30| 192.168.1.100| /reports| 200| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:48:00| 192.168.1.100| /login| 200| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:30:05| 192.168.1.101| /login| 200| Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  
2025-05-15 05:35:10| 192.168.1.101| /profile| 200| Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  
2025-05-15 05:40:00| 192.168.1.102| /login| 200| Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)  
2025-05-15 05:41:30| 192.168.1.102| /settings| 200| Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)  
2025-05-15 05:42:45| 192.168.1.102| /logout| 200| Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(client_ip, function=session(maxpause=15m))

Groups events by the field client_ip into sessions of 15 minutes. then makes a count of the total number of unique sessions 

The [_`maxpause`_](functions-session.html#query-functions-session-maxpause) parameter defines the maximum pause between the sessions (`15m` in this example). Events more far apart than the defined value will become separate sessions. For example, if the same user returns to a site within 15 minutes, it will be the same session. 

  3. logscale
         
         | count()

Makes a count of the total number of unique sessions. 

  4. Event Result set.




##### Summary and Results

The query is used to group events by client IP addresses into sessions of 15m, and then make a count of the total number of unique sessions (returns the total count of sessions across all IP addresses). The query is, for example, useful for measuring unique website/application visitors and understanding real user engagement patterns. Also useful for security monitoring and detection of unusual spikes in unique visitors. 

Sample output from the incoming example data: 

_count  
---  
4  
  
The query counts 4 unique sessions total as the first IP address has activity that spans beyond the 15-minute session timeout, creating two distinct sessions. 

If you make the count on the client_ip field: `| count(client_ip)`, the query will return a more detailed result showing the session count per IP address: 

client_ip| _count  
---|---  
192.168.1.100| 2  
192.168.1.101| 1  
192.168.1.102| 1  
  
#### Create a Pivot Table

**Creating a view of LogScale activity**

##### Query

logscale
    
    
    groupBy([type,actor.user.id],function={groupBy(actor.user.id, function=max(@timestamp))})
    |transpose(header=type)
    |drop(column)

##### Introduction

The [humio-audit](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-audit.html) repository contains audit events for the LogScale cluster. Reporting on this information can provide a wealth of information, but a useful summary can be created based on the activities, users and which the latest user of that particular operation. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy([type,actor.user.id],function={groupBy(actor.user.id, function=max(@timestamp))})

The first step to creating a pivot table is the base query that will create the initial summary of the information. In this fragment, a nested [`groupBy()`](functions-groupby.html "groupBy\(\)") aggregation. The embedded aggregation creates a group of the maximum access time for a given user, by using [`max()`](functions-max.html "max\(\)") on the @timestamp against the actor.user.id. This creates a table of the last event by the user. The outer [`groupBy()`](functions-groupby.html "groupBy\(\)") then creates an aggregation of this maximum user time against the type which defines the operation performed. 

The result is a table of the last user and time for a specific operation; for example, the last time a query was executed. An example of this table can be seen below: 

type |  actor.user.id |  _max  
---|---|---  
`alert.clear-error` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1700546666592   
`alert.create` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1699004139419   
`alert.update` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1700546666676   
`dashboard.create` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1698417330709   
`dataspace.query` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1700721296197   
  
  3. logscale
         
         |transpose(header=type)

The [`transpose()`](functions-transpose.html "transpose\(\)") will convert individual columns into rows, switching the orientation. For example, the type column will now become the type row. However, there are no row titles, so the title for the resulting table will by default create a header row containing the column and row numbers, like this: 

column |  row[1] |  row[2] |  row[3] |  row[4] |  row[5]  
---|---|---|---|---|---  
_max |  1700546666592 |  1699004139419 |  1700546666676 |  1698417330709 |  1700722209214   
actor.user.id |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH   
type |  alert.clear-error |  alert.create |  alert.update |  dashboard.create |  dataspace.query   
  
However, the aggregate grouping, type could be used instead as a valid header for each column. To achieve that, use the [_`header`_](functions-transpose.html#query-functions-transpose-header) parameter to specify type as the column. The resulting table now looks like this: 

alert.clear-error |  alert.create |  alert.update |  column |  dashboard.create |  dataspace.query  
---|---|---|---|---|---  
1700546666592 |  1699004139419 |  1700546666676 |  _max |  1698417330709 |  1700722210073   
0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  actor.user.id |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH   
  
  4. logscale
         
         |drop(column)

The table created contains the summarized information pivoted around the user ID and last event time further summarized by the type of the event. However, there is a column in the table, column, which is now a field in the event stream that was generated from the old row before the table was pivoted. 

That column can be removed by dropping the column field from the event using [`drop()`](functions-drop.html "drop\(\)") to remove the column from the events. 

  5. Event Result set.




##### Summary and Results

Pivoting an event set of data allows for the information to be displayed and summarized in a format that may make more logical sense as a display format. The final table will look like this: 

alert.clear-error |  alert.create |  alert.update |  dashboard.create |  dataspace.query   
---|---|---|---|---  
1700546666592 |  1699004139419 |  1700546666676 |  1698417330709 |  1700722210073   
0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH   
  
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
  
#### Filter Out Fields With No Value

**Filter out fields with no values from search results**

##### Query

logscale
    
    
    method=GET
    groupBy(field=[method, statuscode], function=count(as=method_total))
    sort([method, statuscode], order=asc)
    FieldName!=""

##### Introduction

It is possible to filter out on fields with no values in a given returned search result. In this example, all statuscode fields containing no value is filtered out from the final search result. 

Example incoming data might look like this: 

method| statuscode| method_total  
---|---|---  
GET| <no value>| 10  
GET| 200| 32492  
GET| 301| 1  
GET| 304| 113  
GET| 403| 9  
GET| 404| 132  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         method=GET

Filters for all events with methods of the type `GET`. 

  3. logscale
         
         groupBy(field=[method, statuscode], function=count(as=method_total))

Groups the returned results into a method field and a statuscode field and makes a count of the events in a new field named method_total. 

  4. logscale
         
         sort([method, statuscode], order=asc)

Sorts the returned results in ascending order. 

  5. logscale
         
         FieldName!=""

Excludes all events where one of the fields do not contain a value. 

  6. Event Result set.




##### Summary and Results

The query is used to filter out fields not containing any values from the returned search result. 

Sample output from the incoming example data: 

method| statuscode| method_total  
---|---|---  
GET| 200| 32492  
GET| 301| 1  
GET| 304| 113  
GET| 403| 9  
GET| 404| 132  
  
#### Find Fields With Data in Class

****

##### Query

**Search Repository:** [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html)

logscale
    
    
    wildcard(field=class,pattern="*Data*")
    | groupBy(class)

##### Introduction

Find all events containing any `Data` string in their class, and count the occurrences for each class that is found. For example, it can be used to get a list of events that have items such as DataIngestRateMonitor, or LocalDatasource. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         wildcard(field=class,pattern="*Data*")

Searches the incoming data to list all events having Data (and everything around it) in their string. 

  3. logscale
         
         | groupBy(class)

Takes the events extracted from the search and groups them by the class field. 

  4. Event Result set.




##### Summary and Results

The result is an aggregated count of all events matching anything with `Data` (with one or more characters before or after), in the class field. 

class| _count  
---|---  
c.h.c.c.ChatterDataMemoryStatusLoggerJob$| 283  
c.h.d.DataIngestRateMonitor$| 7504  
c.h.d.LocalDatasource$| 10352  
c.h.d.q.EmptyIdleDatasourcesCleaner| 3  
c.h.e.e.Datasource$| 3947  
c.h.e.e.Datasources$| 4  
c.h.e.f.DataSnapshotOps$| 662  
c.h.e.f.DataWithGlobal| 7254  
c.h.j.CleanupDatasourceFilesJob| 141  
c.h.j.DataSyncJobImpl$| 46594  
c.h.j.DatasourceRehashingJob$| 32  
c.h.k.ChatterDataDistributionKafka$| 107  
  
#### Find Fields With S3Bucket in Class

****

##### Query

**Search Repository:** [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html)

logscale
    
    
    wildcard(field=class, pattern="*S3Bucket*", ignoreCase=true)
    | groupBy(class)

##### Introduction

Find all events containing any `S3Bucket` item (and all before and after) in their class, and count the occurrences for each class that is found. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         wildcard(field=class, pattern="*S3Bucket*", ignoreCase=true)

Searches the incoming data to list all events having S3Bucket (or everything around it, case-insensitive) in their string. 

  3. logscale
         
         | groupBy(class)

Takes the events extracted from the search and group them by the class field. 

  4. Event Result set.




##### Summary and Results

The result is an aggregated count of all events matching anything with `S3Bucket`, case-insensitive, in the class field. 

class| _count  
---|---  
c.h.b.s.S3BucketStorageCleaningJob| 197  
c.h.b.s.S3BucketStorageFileUpLoader| 2329  
c.h.b.s.S3BucketStorageUploadJob| 3869  
  
![Searching S3Bucket with wildcard\(\)](images/query-functions/wildcard-s3-bucket.png)  
---  
  
**Figure 149. Search S3Bucket With wildcard()**

  


#### Find Matches in Array Given a Regular Expression - Example 1

**Use regular expressions to search for and match specific patterns in flat arrays**

##### Query

logscale
    
    
    array:regex("incidents[]", regex="^Cozy Bear.*")
    | groupBy(host)

##### Introduction

In this example, the regular expression is used to search for patterns where the value `Cozy Bear` appears in a certain position across arrays. 

Example incoming data might look like this: 

host| incidents[0]| incidents[1]| incidents[2]  
---|---|---|---  
v1| Evil Bear| Cozy Bear|   
v15| Fancy Fly| Tiny Cat| Cozy Bears  
v22| Fancy Fly| Tiny Cat| Cold Bears  
v4| Fancy Fly| Tiny Cat| Cozy Bearskins  
v1| Evil Bear| Cozy Bears|   
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:regex("incidents[]", regex="^Cozy Bear.*")

Searches in the incidents array for values that only start with `Cozy Bear`. Find all matches given that regular expression. 

  3. logscale
         
         | groupBy(host)

Groups the returned results by host. 

  4. Event Result set.




##### Summary and Results

The query using the regex expression are used to quickly search and return results for specific values in arrays. Regular expressions are useful when searching for different strings containing the same patterns; such as social security numbers, URLs, email addresses, and other strings that follow a specific pattern. 

Sample output from the incoming example data: 

host| _count  
---|---  
v1| 2  
v15| 1  
v4| 1  
  
#### Find Matches in Array Given a Regular Expression - Example 2

**Use regular expressions to search for and match specific patterns ignoring case in flat arrays**

##### Query

logscale
    
    
    array:regex("responses[]", regex="bear$", flags="i")

##### Introduction

In this example, the regular expression is used to search for patterns where the value `bear` appears at the end of a value in an array element, ignoring the case. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:regex("responses[]", regex="bear$", flags="i")

Searches in the responses array for values that begins with `bear`, ignoring the case (due to the [`i`](functions-array-regex.html#query-functions-array-regex-flags-value-i) flag). 

  3. Event Result set.




##### Summary and Results

The queries using the regex expression are used to quickly search and return results for specific values in arrays. Regular expressions are useful when searching for different strings containing the same patterns; such as social security numbers, URLs, email addresses, and other strings that follow a specific pattern. 

#### Find Minimum And Maximum Values of any Numerical Field in Session

**Find minimum and maximum values of any numerical field in a session using the[`session()`](functions-session.html "session\(\)") function **

##### Query

logscale
    
    
    groupBy(cookie_id, function=session([max(bet),min(bet)]))

##### Introduction

In this example, the [`session()`](functions-session.html "session\(\)") function is used to find minimum and maximum values of the field bet in a session. The [`session()`](functions-session.html "session\(\)") function groups events by a given timespan. 

Example incoming data might look like this: 

timestamp| cookie_id| bet| action_type| category  
---|---|---|---|---  
2025-05-15 05:30:00| user123| 25.99| purchase| electronics  
2025-05-15 05:32:00| user123| 49.99| purchase| electronics  
2025-05-15 05:34:00| user123| 15.99| purchase| accessories  
2025-05-15 05:48:00| user123| 99.99| purchase| appliances  
2025-05-15 05:49:00| user123| 150.00| purchase| furniture  
2025-05-15 05:35:00| user456| 75.50| purchase| clothing  
2025-05-15 05:37:00| user456| 199.99| purchase| appliances  
2025-05-15 05:40:00| user456| 89.99| purchase| electronics  
2025-05-15 05:30:00| user789| 10.99| purchase| books  
2025-05-15 05:55:00| user789| 20.99| purchase| books  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(cookie_id, function=session([max(bet),min(bet)]))

Groups events by the field cookie_id (unique user identifier) and creates sessions of 15-minutes timeout (the default value of the [_`maxpause`_](functions-session.html#query-functions-session-maxpause) parameter), then calculates the maximum and minimum values of the field bet for each session, returning the results in new fields named _max and _min. 

  3. Event Result set.




##### Summary and Results

The query is used to analyze the likelihood (the bet) of the behavior within user sessions. This query is, for example, useful for identifying if the event was an attempt to hack the system. 

Sample output from the incoming example data: 

cookie_id| _max| _min  
---|---|---  
user123| 49.99| 15.99 // First session  
user123| 150.00| 99.99 // Second session  
user456| 199.99| 75.50 // Single session  
user789| 10.99| 10.99 // First session  
user789| 20.99| 20.99 // Second session  
  
Note that each session shows its own min/max values. 

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

#### Find Processes with Low Execution Count

**Group processes by hash and name to identify rarely executed ones using the[`groupBy()`](functions-groupby.html "groupBy\(\)") function **

##### Query

logscale
    
    
    #event_simpleName=ProcessRollup2 OR #event_simpleName=SyntheticProcessRollup2
    aid=?aid
    groupBy([SHA256HashData, ImageFileName], limit=max)
    _count < 5
    sort(_count, limit=1000)

##### Introduction

In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") function is used to identify processes that have been executed only a few times on a specific host, which could be useful for detecting unusual or potentially suspicious activity. 

Example incoming data might look like this: 

@timestamp| event_simpleName| aid| SHA256HashData| ImageFileName| CommandLine  
---|---|---|---|---|---  
2025-10-06T10:00:00Z| ProcessRollup2| 12345abc| a1b2c3d4e5f6...| chrome.exe| C:\Program Files\Google\Chrome\Application\chrome.exe  
2025-10-06T10:05:00Z| ProcessRollup2| 12345abc| a1b2c3d4e5f6...| chrome.exe| C:\Program Files\Google\Chrome\Application\chrome.exe  
2025-10-065T10:10:00Z| SyntheticProcessRollup2| 12345abc| f6e5d4c3b2a1...| suspicious.exe| C:\Users\Admin\Downloads\suspicious.exe  
2025-10-06T10:15:00Z| ProcessRollup2| 12345abc| 98765432dcba...| notepad.exe| C:\Windows\System32\notepad.exe  
2025-10-06T10:20:00Z| ProcessRollup2| 12345abc| 98765432dcba...| notepad.exe| C:\Windows\System32\notepad.exe  
2025-10-06T10:25:00Z| ProcessRollup2| 12345abc| 11223344aabb...| calc.exe| C:\Windows\System32\calc.exe  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #event_simpleName=ProcessRollup2 OR #event_simpleName=SyntheticProcessRollup2

Filters events to include only process execution events with event_simpleName equal to `ProcessRollup2` or `SyntheticProcessRollup2`. 

  3. logscale
         
         aid=?aid

Filters events for a specific host using the aid (agent ID) parameter. 

  4. logscale
         
         groupBy([SHA256HashData, ImageFileName], limit=max)

Groups events by both the SHA256HashData and ImageFileName fields. The [_`limit`_](functions-groupby.html#query-functions-groupby-limit) parameter is set to `max` to ensure all groups are included. 

By default the [`count()`](functions-count.html "count\(\)") function is used and the grouped count returned in a field named _count. 

  5. logscale
         
         _count < 5

Filters the groups to show only those with fewer than 5 executions, using the built-in _count field that is automatically created by [`groupBy()`](functions-groupby.html "groupBy\(\)"). 

  6. logscale
         
         sort(_count, limit=1000)

Sorts the results by execution count in ascending order, limiting the output to 1000 results. 

  7. Event Result set.




##### Summary and Results

The query is used to identify processes that have been executed infrequently on a specific host by grouping them based on their hash value and image name. 

This query is useful, for example, to detect potentially suspicious or unusual processes that do not run often, which could indicate malicious activity or unauthorized software installations. 

Sample output from the incoming example data: 

SHA256HashData| ImageFileName| _count  
---|---|---  
f6e5d4c3b2a1...| suspicious.exe| 1  
11223344aabb...| calc.exe| 1  
98765432dcba...| notepad.exe| 2  
  
The results are sorted by execution count, showing the least frequently executed processes first. Each row represents a unique combination of process hash and name, along with how many times it was executed. 

Processes with the same name but different hashes are treated as separate entries, helping identify potentially malicious files masquerading as legitimate processes. 

#### Get List of Status Codes

**Get list of status codes returned and a count of each for a given period using the[`groupBy()`](functions-groupby.html "groupBy\(\)") function with [`count()`](functions-count.html "count\(\)") **

##### Query

logscale
    
    
    groupBy(field=status, function=count())

##### Introduction

In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") function is used to get a list of status codes for logged events. For instance, the status code `200` is returned when the request is successful, and `404` when the page is not found. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(field=status, function=count())

Groups events by the status field, and counts the number of events in each group. 

It is possible to enhance the query for more detailed analysis. The following query example groups by both the fields status and source, limits to 1000 results, and sorts by count descending. `groupBy([field=status, field=source], function=count(), limit=1000) | sort(_count, order=desc)`

  3. Event Result set.




##### Summary and Results

The query is used to extract a list of status codes, each with a count of how many events have that status. The query is useful for summarizing and analyzing log data. 

Sample output from the incoming example data: 

status| _count  
---|---  
101| 17  
200| 46183  
204| 3  
307| 1  
400| 2893  
401| 4  
Failure| 1  
Success| 8633  
  
#### Group Events by Single Field

**Basic grouping of events by status_code field using the [`groupBy()`](functions-groupby.html "groupBy\(\)") function **

##### Query

logscale
    
    
    groupBy(status_code)

##### Introduction

In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") is used to group events by their status codes to analyze the distribution of different response statuses. 

Example incoming data might look like this: 

@timestamp| status_code| endpoint| response_time  
---|---|---|---  
1686837825000| 200| /api/users| 145  
1686837826000| 404| /api/products| 89  
1686837827000| 200| /api/orders| 167  
1686837828000| 500| /api/payment| 890  
1686837829000| 200| /api/users| 156  
1686837830000| 404| /api/items| 78  
1686837831000| 200| /api/orders| 178  
1686837832000| 500| /api/checkout| 923  
1686837833000| 200| /api/products| 134  
1686837834000| 404| /api/users| 92  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(status_code)

Groups events by unique values in the status_code field. When used without any aggregate functions, [`groupBy()`](functions-groupby.html "groupBy\(\)") automatically creates a field named _count showing the number of events for each unique value. 

It is the same as: `groupBy(status_code, function=count())`

  3. Event Result set.




##### Summary and Results

The query is used to analyze the distribution of status codes across all events. 

The _count field is automatically added to show the number of events in each group. 

This query is useful, for example, to monitor system health, identify error patterns, or track the frequency of different response types in a service. 

For other examples with [`groupBy()`](functions-groupby.html "groupBy\(\)"), see [`groupBy()` Syntax Examples](functions-groupby.html#functions-groupby-syntax-examples "groupBy\(\) Syntax Examples"). 

Sample output from the incoming example data: 

status_code| _count  
---|---  
200| 5  
404| 3  
500| 2  
  
#### Group Events by Single Field Without Count

**Basic grouping of events by status_code field with explicit empty [_`function`_](functions-groupby.html#query-functions-groupby-function) parameter using the [`groupBy()`](functions-groupby.html "groupBy\(\)") function **

##### Query

logscale
    
    
    groupBy(status_code, function=[])

##### Introduction

In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") is used to group events by their status codes without calculating count. 

Example incoming data might look like this: 

@timestamp| status_code| endpoint| response_time  
---|---|---|---  
1686837825000| 200| /api/users| 145  
1686837826000| 404| /api/products| 89  
1686837827000| 200| /api/orders| 167  
1686837828000| 500| /api/payment| 890  
1686837829000| 200| /api/users| 156  
1686837830000| 404| /api/items| 78  
1686837831000| 200| /api/orders| 178  
1686837832000| 500| /api/checkout| 923  
1686837833000| 200| /api/products| 134  
1686837834000| 404| /api/users| 92  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(status_code, function=[])

Groups events by unique values in the status_code field. The empty function array ([_`function`_](functions-groupby.html#query-functions-groupby-function)=`[]`) prevents automatic counting. 

This approach helps conserve memory while identifying the unique status codes in the events. 

  3. Event Result set.




##### Summary and Results

The query is used to identify unique field values (in this case different status codes) while minimizing memory usage. 

This query is useful, for example, to quickly discover unique values in large event sets and support initial data exploration before detailed analysis. 

For other examples with [`groupBy()`](functions-groupby.html "groupBy\(\)"), see [`groupBy()` Syntax Examples](functions-groupby.html#functions-groupby-syntax-examples "groupBy\(\) Syntax Examples"). 

Sample output from the incoming example data: 

status_code  
---  
200  
404  
500  
  
#### Group First Events by Log Level

**Limit and group events using[`head()`](functions-head.html "head\(\)") and [`groupBy()`](functions-groupby.html "groupBy\(\)") functions **

##### Query

logscale
    
    
    head(limit=10)
    groupBy(loglevel)

##### Introduction

In this example, the [`head()`](functions-head.html "head\(\)") function is used to limit the result set to 100 events, which are then grouped by their log level using the [`groupBy()`](functions-groupby.html "groupBy\(\)") function. 

Example incoming data might look like this: 

@timestamp| loglevel| service| message| status_code  
---|---|---|---|---  
2025-09-01T10:00:00Z| ERROR| authentication| Failed login attempt| 401  
2025-09-01T10:00:05Z| INFO| authentication| Successful login| 200  
2025-09-01T10:00:10Z| ERROR| database| Connection timeout| 503  
2025-09-01T10:00:15Z| WARN| api| Rate limit approaching| 429  
2025-09-01T10:00:20Z| ERROR| authentication| Invalid token| 401  
2025-09-01T10:00:25Z| INFO| api| Request processed| 200  
2025-09-01T10:00:30Z| DEBUG| database| Query executed| 200  
2025-09-01T10:00:35Z| ERROR| api| Internal error| 500  
2025-09-01T10:00:40Z| INFO| authentication| User logout| 200  
2025-09-01T10:00:45Z| WARN| database| High CPU usage| 200  
2025-09-01T10:00:50Z| DEBUG| api| Cache hit| 200  
2025-09-01T10:00:55Z| ERROR| authentication| Session expired| 401  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         head(limit=10)

Returns the first 10 events from the dataset. The [_`limit`_](functions-head.html#query-functions-head-limit) parameter explicitly specifies the number of events to return. The events are returned in the order they were received, starting from the oldest event in the time range. 

  3. logscale
         
         groupBy(loglevel)

Groups the events by the values in the loglevel field. The [`groupBy()`](functions-groupby.html "groupBy\(\)") function creates buckets for each unique value and counts the number of events in each bucket. By default, it creates a field named _count containing the number of events in each group. 

  4. Event Result set.




##### Summary and Results

The query is used to analyze the distribution of log levels across the first 10 events in the dataset. If `head(limit=100)` it would have returned 100 events. 

This query is useful, for example, to quickly assess the proportion of different log levels in a sample of events or to identify if there is an unusual distribution of log severities. 

Sample output from the incoming example data: 

loglevel| _count  
---|---  
ERROR| 5  
INFO| 3  
WARN| 2  
DEBUG| 2  
  
Note that the output shows the count of events for each log level found within the first 10 events, providing a quick overview of the log level distribution in the sample. 

#### Group HTTP Methods and Count Status Codes

**Analyze HTTP traffic patterns using nested[`groupBy()`](functions-groupby.html "groupBy\(\)") function **

##### Query

logscale
    
    
    groupBy(method, function=[count(as=method_total),
            groupBy(statuscode, function=count(as=method_status_count))])

##### Introduction

In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") function is used to analyze HTTP traffic patterns by grouping requests first by HTTP method and then by status code, providing counts at both levels. 

Example incoming data might look like this: 

@timestamp| method| statuscode| path| bytes  
---|---|---|---|---  
2025-08-06T10:00:00Z| GET| 200| /index.html| 1024  
2025-08-06T10:00:01Z| POST| 201| /api/users| 512  
2025-08-06T10:00:02Z| GET| 404| /missing.html| 256  
2025-08-06T10:00:03Z| GET| 200| /about.html| 768  
2025-08-06T10:00:04Z| POST| 400| /api/users| 128  
2025-08-06T10:00:05Z| PUT| 200| /api/users/1| 896  
2025-08-06T10:00:06Z| GET| 200| /contact.html| 645  
2025-08-06T10:00:07Z| POST| 201| /api/orders| 789  
2025-08-06T10:00:08Z| GET| 404| /old-page.html| 234  
2025-08-06T10:00:09Z| DELETE| 204| /api/users/2| 0  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(method, function=[count(as=method_total),
                 groupBy(statuscode, function=count(as=method_status_count))])

Groups events first by the [method](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html) field and performs two functions: 

     * Counts the total number of events for each HTTP method using [`count()`](functions-count.html "count\(\)") and returns the result in a new field named method_total. 

     * Creates a nested grouping by statuscode within each method group, counting occurrences using [`count()`](functions-count.html "count\(\)") and returns the result in a new field named method_status_count. 

  3. Event Result set.




##### Summary and Results

The query is used to analyze HTTP traffic patterns by providing a hierarchical view of request methods and their associated status codes. 

This query is useful, for example, to identify patterns in API usage, detect potential issues with specific HTTP methods, or monitor the distribution of success and error responses across different request types. 

Sample output from the incoming example data: 

method| method_total| statuscode| method_status_count  
---|---|---|---  
GET| 5| 200| 3  
GET| 5| 404| 2  
POST| 3| 201| 2  
POST| 3| 400| 1  
PUT| 1| 200| 1  
DELETE| 1| 204| 1  
  
Note that the output shows both the total count per method (method_total) and the breakdown of status codes (method_status_count) within each method, providing a comprehensive view of the HTTP traffic distribution. 

This data would be effectively visualized using a Sankey diagram widget to show the flow from HTTP methods to status codes, or a nested pie chart to display the distribution. 

#### Group HTTP Methods and Status Codes Using Nested [`groupBy()`](functions-groupby.html "groupBy\(\)")

**Analyze HTTP traffic patterns by method and status code using the[`groupBy()`](functions-groupby.html "groupBy\(\)") function **

##### Query

logscale
    
    
    groupBy(method, function=[count(as=method_total), groupBy(statuscode, function=count(as=method_status_count))])

##### Introduction

In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") function is used to analyze HTTP traffic patterns by grouping requests first by HTTP method and then by status code within each method. 

Example incoming data might look like this: 

@timestamp| method| statuscode| path| bytes  
---|---|---|---|---  
2025-08-06T10:00:00Z| GET| 200| /index.html| 1024  
2025-08-06T10:00:01Z| POST| 201| /api/users| 512  
2025-08-06T10:00:02Z| GET| 404| /missing.html| 256  
2025-08-06T10:00:03Z| GET| 200| /about.html| 768  
2025-08-06T10:00:04Z| POST| 400| /api/users| 128  
2025-08-06T10:00:05Z| PUT| 200| /api/users/1| 384  
2025-08-06T10:00:06Z| GET| 200| /contact.html| 896  
2025-08-06T10:00:07Z| DELETE| 204| /api/users/2| 0  
2025-08-06T10:00:08Z| GET| 500| /error.html| 1024  
2025-08-06T10:00:09Z| POST| 201| /api/orders| 756  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(method, function=[count(as=method_total), groupBy(statuscode, function=count(as=method_status_count))])

Groups events by the [method](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html) field and performs two aggregations: 

     * Counts total events for each HTTP method using [`count()`](functions-count.html "count\(\)"), and returns the result in a new field named method_total. 

     * Creates a nested grouping by statuscode within each method group, counting occurrences using [`count()`](functions-count.html "count\(\)") and returns the result in a new field named method_status_count. 

  3. Event Result set.




##### Summary and Results

The query is used to analyze HTTP traffic patterns by providing a hierarchical view of request methods and their associated status codes. 

This query is useful, for example, to identify patterns in API usage, detect potential issues with specific HTTP methods, or monitor the distribution of success and error responses across different request types. 

Sample output from the incoming example data: 

method| method_total| statuscode| method_status_count  
---|---|---|---  
GET| 5| 200| 3  
GET| 5| 404| 1  
GET| 5| 500| 1  
POST| 3| 201| 2  
POST| 3| 400| 1  
PUT| 1| 200| 1  
DELETE| 1| 204| 1  
  
Note that the output shows the total count for each HTTP method in method_total and a breakdown of status codes and their counts within each method in method_status_count. 

This data is well-suited for visualization using a Sankey diagram widget, which can effectively show the flow from HTTP methods to status codes. 

#### Hourly Data Events

**Summarize events by providing a count of the number of data events per hour using the[`time:hour()`](functions-time-hour.html "time:hour\(\)") function **

##### Query

logscale
    
    
    hr := time:hour(field="@ingesttimestamp")
    |groupBy(hr)

##### Introduction

In this example, the [`time:hour()`](functions-time-hour.html "time:hour\(\)") function is used with [`groupBy()`](functions-groupby.html "groupBy\(\)") to average the count of data events per hour. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         hr := time:hour(field="@ingesttimestamp")

Gets the hour (24-hour clock) of the values in the @ingesttimestamp and returns the results in a new field named `hr`. 

  3. logscale
         
         |groupBy(hr)

Groups the returned results by hr field and provides a count of the number of data events per hour in a _count field. 

  4. Event Result set.




##### Summary and Results

The query is used to average the count of data events per hour. The results can be plotted onto a bar chart. 

#### List All EC2 Hosts With FirstSeen Data Within 14 Days

**List all the EC2 hosts with FirstSeen data within 14 days using the[`groupBy()`](functions-groupby.html "groupBy\(\)") function with [`selectLast()`](functions-selectlast.html "selectLast\(\)") **

##### Query

logscale
    
    
    #repo=sensor_metadata #data_source_name=aidmaster cloud.provider = "AWS_EC2_V2"
    | groupBy([aid], function=(selectLast([event_platform, aid, ComputerName, AgentVersion, FirstSeen])), limit=max)
    | FirstSeen := formatTime("%FT%T%z", field=FirstSeen)
    | TimeDelta := now() - duration("14d")

##### Introduction

In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") function is used with [`selectLast()`](functions-selectlast.html "selectLast\(\)") to retrieve the latest information about `AWS EC2` instances running CrowdStrike sensors, showing their platform, hostname, agent version, and when they were first seen, with a 14-day reference point for age comparison. 

Example incoming data (raw data in sensor_metadata) might look like this: 

@timestamp| aid| cloud.provider| event_platform| ComputerName| AgentVersion| FirstSeen  
---|---|---|---|---|---|---  
2025-05-20T10:00:00Z| 1234abcd| AWS_EC2_V2| Windows| ec2-web-01| 6.45.15678| 2025-01-15T08:30:00Z  
2025-05-21T11:00:00Z| 1234abcd| AWS_EC2_V2| Windows| ec2-web-01| 6.45.15679| 2025-01-15T08:30:00Z  
2025-05-22T12:00:00Z| 5678efgh| AWS_EC2_V2| Linux| ec2-app-02| 6.45.15678| 2025-02-01T14:45:00Z  
2025-05-23T13:00:00Z| 5678efgh| AWS_EC2_V2| Linux| ec2-app-02| 6.45.15679| 2025-02-01T14:45:00Z  
2025-05-24T14:00:00Z| 90123ijk| AWS_EC2_V2| Windows| ec2-db-03| 6.45.15678| 2025-03-10T09:15:00Z  
2025-05-25T15:00:00Z| 90123ijk| AWS_EC2_V2| Windows| ec2-db-03| 6.45.15679| 2025-03-10T09:15:00Z  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #repo=sensor_metadata #data_source_name=aidmaster cloud.provider = "AWS_EC2_V2"

Searches in the sensor_metadata repository, and filters for #data_source_name fields containing the value `aidmaster`, looking for cloud.provider of the type `AWS_EC2_V2` only. 

  3. logscale
         
         | groupBy([aid], function=(selectLast([event_platform, aid, ComputerName, AgentVersion, FirstSeen])), limit=max)

Groups results by the field aid (Agent ID). Then, for each unique group, selects the most recent values for the fields: event_platform, aid, ComputerName, AgentVersion, FirstSeen. 

Using the [`selectLast()`](functions-selectlast.html "selectLast\(\)") within the [`groupBy()`](functions-groupby.html "groupBy\(\)") is what actually selects the most recent record for each group. 

  4. logscale
         
         | FirstSeen := formatTime("%FT%T%z", field=FirstSeen)

Formats the timestamp in the FirstSeen field into ISO 8601 format. The result is stored back in the FirstSeen field. 

  5. logscale
         
         | TimeDelta := now() - duration("14d")

Calculates timestamp from 14 days ago, and returns the results into a new field named TimeDelta. The calculation is done by subtracting a 14-day duration from the current time using [`duration()`](functions-duration.html "duration\(\)"). 

This new TimeDelta field that represents a timestamp from 14 days ago, can be used for filtering or comparing against the FirstSeen timestamps. 

  6. Event Result set.




##### Summary and Results

The query is used to retrieve the latest information about AWS EC2 instances running CrowdStrike sensors, showing their platform, hostname, agent version, and when they were first seen, with a 14-day reference point for age comparison. 

The query is useful, for example, for auditing EC2 instance coverage, identifying newly added EC2 instances within the last two weeks, monitoring sensor versions or identifying aging or outdated installations. 

Sample output from the incoming example data: 

aid| event_platform| ComputerName| AgentVersion| FirstSeen| TimeDelta  
---|---|---|---|---|---  
1234abcd| Windows| ec2-web-01| 6.45.15679| 2025-01-15T08:30:00+0000| 2025-05-12T13:06:56+0000  
5678efgh| Linux| ec2-app-02| 6.45.15679| 2025-02-01T14:45:00+0000| 2025-05-12T13:06:56+0000  
90123ijk| Windows| ec2-db-03| 6.45.15679| 2025-03-10T09:15:00+0000| 2025-05-12T13:06:56+0000  
  
Each aid appears only once with its most recent values. Note that TimeDelta value is based on the current date provided (Mon, 26 May 2025 13:06:56 GMT). 

#### Preview Content in a Lookup File With [`readFile()`](functions-readfile.html "readFile\(\)") and Filter With ![`join()`](functions-join.html "join\(\)")

**Preview content in a lookup file in the search portion of a repo and filter for specific data with the ![`join()`](functions-join.html "join\(\)") function **

##### Query

logscale
    
    
    readFile("host_names.csv")
    | !join(query={groupBy(host_name)}, field=host_name, key=host_name, include=[host_name, id])

##### Introduction

In this example, the [`readFile()`](functions-readfile.html "readFile\(\)") function is used to look up a host_names.csv file, and then filter for host names that do not send any logs. 

Example incoming data might look like this: 
    
    
    |--------------------|
    | host_name, host_id |
    | DESKTOP-VSKPBK8, 1 |
    | FINANCE, 2         |
    | homer-xubuntu, 3   |
    | logger, 4          |
    | DESKTOP-1, 5       |
    | DESKTOP-2, 6       |
    | DESKTOP-3, 7       |
    |--------------------|

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         readFile("host_names.csv")

Displays the content of the .csv file. 

  3. logscale
         
         | !join(query={groupBy(host_name)}, field=host_name, key=host_name, include=[host_name, id])

Filters for host names that do not send any logs. 

  4. Event Result set.




##### Summary and Results

The query is used to preview content in CSV Lookup Files, and then filter for host names that do not send any logs. 

Sample output from the incoming example data: 

host_id| host_name  
---|---  
5| DESKTOP-1  
6| DESKTOP-2  
7| DESKTOP-3  
  
#### Search Accross Multiple Structured Fields

**Search across multiple structured fields using the transpose() function within groupBy()**

##### Query

logscale
    
    
    groupBy(@id, function=transpose())
    | row[1] = /httpd/
    | groupBy(column)

##### Introduction

By transposing event set, the information can be viewed and summarized in a more human readable form. In this example, the [`transpose()`](functions-transpose.html "transpose\(\)") function is used within a [`groupBy()`](functions-groupby.html "groupBy\(\)") function to search across multiple structured fields in the [HUMIO](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository. 

Example incoming data might look like this: 

host| @rawstring  
---|---  
MAIL01| 2025-03-18T10:14:47.142Z MAIL01 httpd[61789]: 192.168.0.198 - - [2025-03-13:23:05:48 +0800] "GET /api/v2/products/search HTTP/1.1" 200 33456  
LON-SRV01| 2025-03-18T10:14:46.940Z LON-SRV01 httpd[60123]: 192.168.0.198 - - [2025-03-13:20:50:14 +0500] "GET /uploads/documents/terms.pdf HTTP/1.1" 401 36912  
MAIL01| 2025-03-18T10:14:46.691Z MAIL01 httpd[51234]: 192.168.0.198 - - [2025-03-13:12:50:16 -0300] "GET /downloads/mobile/app-v2.1.apk HTTP/1.1" 403 1234  
SYD-SRV01| 2025-03-18T10:14:46.542Z SYD-SRV01 httpd[45678]: 192.168.1.123 - - [2025-03-13:19:30:17 +0400] "GET /uploads/avatars/default.png HTTP/1.1" 404 61789  
PROD-SQL01| 2025-03-18T10:14:46.141Z PROD-SQL01 httpd[56789]: 192.168.1.245 - - [2025-03-13:17:30:38 +0200] "GET /uploads/avatars/default.png HTTP/1.1" 200 13456  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(@id, function=transpose())

Groups events by unique @id values, applies the [`transpose()`](functions-transpose.html "transpose\(\)") function for each group, converting row values into column headers. A new row-based structure for each @id field is created. 

After using [`transpose()`](functions-transpose.html "transpose\(\)"), the data might look like this: 

@id| column| row[1]  
---|---|---  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| @timezone| Z  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| app| httpd[56789]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| host| PROD-SQL01  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886,msg, 192.168.1.245 - - [2025-03-13:17:30:38 +0200] "GET /uploads/avatars/default.png HTTP/1.1" 200 13456|  |   
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| priority| 34  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| version| 1  
  
  3. logscale
         
         | row[1] = /httpd/

Filters for events where row[1] regex matches the value `httpd`. 

After filtering, the data might look like this (@rawstring has been removed from the below for clarity): 

@id| column| row[1]  
---|---|---  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| app| httpd[56789]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_528_1742292886| app| httpd[45678]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_531_1742292886| app| httpd[51234]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_536_1742292886| app| httpd[60123]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_540_1742292887| app| httpd[61789]:  
  
  4. logscale
         
         | groupBy(column)

Groups results by the column field, showing which original fields contained the value `httpd`, and makes a count of matches per field, returning the counted results in a field named _count. The final groupBy(column) removes duplicate entries. 

  5. Event Result set.




##### Summary and Results

The query is used to search across multiple structured fields in the [HUMIO](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository to show where `httpd` appears most often. It makes results more readable, identifies field patterns, and is very useful for statistical analysis. 

Sample output from the incoming example data: 

column| _count  
---|---  
@rawstring| 5  
app| 5  
  
#### Transpose a Basic Table

**Transposing an event set effectively switches rows (each event) into columns (an event)**

##### Query

logscale
    
    
    groupBy([loglevel])
    | transpose(header=loglevel)
    | drop(column)

##### Introduction

By transposing event set, the information can be viewed and summarized in a more human readable form. Transposing also allows for aggregated data to be viewed in a form where the value of an aggregated field becomes the columns. This can be used to summarize the information further by showing multiple rows of data. For example, in the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository the event information contains a list of errors, warnings, or informational events for activity within the cluster. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy([loglevel])

Aggregates the lows by the loglevel. This field will either be `WARN`, `ERROR` or `INFO` depending on the level of the event log entry. The default function is used, which results in a count in the number of times an event of this type has been seen: 

loglevel |  _count  
---|---  
`ERROR` |  27424   
`INFO` |  18840156   
`WARN` |  2059898   
  
In this output, each event is a row in the table, each with two fields, loglevel and _count. 

  3. logscale
         
         | transpose(header=loglevel)

Transposing the events within the [`transpose()`](functions-transpose.html "transpose\(\)") will make each field in each event a row in the new stream of events, for example, the loglevel field with the value `ERROR` will become the field ERROR, swapping the rows for columns. By using the [_`header`_](functions-transpose.html#query-functions-transpose-header) parameter, [`transpose()`](functions-transpose.html "transpose\(\)") uses the value of the aggregated field as the fieldname. The output will now be a table with a column (field) for each value, and a single row with the count: 

ERROR |  INFO |  WARN |  column  
---|---|---|---  
97159 |  63719404 |  5716733 |  _count   
  
  4. logscale
         
         | drop(column)

In the final output, the column field in the events is the one generated from the field names of the original events and it's not needed, so it can be removed by using the [`drop()`](functions-drop.html "drop\(\)") function to remove the field from the event set. 

  5. Event Result set.




##### Summary and Results

The [`transpose()`](functions-transpose.html "transpose\(\)") is a great way of reorganizing data into a format is either more readable, or easily applied to other display formats as part of a widget. The final table looks like this: 

ERROR |  INFO |  WARN  
---|---|---  
97159 |  63719404 |  5716733   
  
However, the information as it is now formatted can more easily be applied to a variety of visualizations. For example, the data can be formatted as a bar chart, as we now have a list of fields and a value: 

![](images/functions/examples/transpose/transpose-basic-bar.png)  
---  
  
The difference is that without [`transpose()`](functions-transpose.html "transpose\(\)"), the aggregate result set is a list of events with a field name and value. With [`transpose()`](functions-transpose.html "transpose\(\)"), the result set is a single event with multiple fields, and this is interpreted by the bar chart as a series of values.
