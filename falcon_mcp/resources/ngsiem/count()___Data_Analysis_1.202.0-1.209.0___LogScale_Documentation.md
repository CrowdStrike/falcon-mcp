# count() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-count.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Feb 3, 2025

## [`count()`](functions-count.html "count\(\)")

Counts the number of events in the repository, or streaming through the function. You can use this field name to pipe the results to other query functions or general use. 

It's possible to specify a field and only events containing that field are counted. It's also possible to do a distinct count. When having many distinct values LogScale will not try to keep them all in memory. An estimate is then used, so the result will not be a precise match. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-count.html#query-functions-count-as)|  string| optional[a] | `_count`|  The name of the output field.   
[_`distinct`_](functions-count.html#query-functions-count-distinct)|  boolean| optional[[a]](functions-count.html#ftn.table-functions-count-optparamfn) |  |  When specified, counts only distinct values. When this parameter is set to `true`, LogScale always uses an estimate, which may give an inexact result as the value.   
[_`field`_](functions-count.html#query-functions-count-field)[b]| string| optional[[a]](functions-count.html#ftn.table-functions-count-optparamfn) |  |  The field for which only events are counted.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-count.html#query-functions-count-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-count.html#query-functions-count-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     count("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     count(field="value")
> 
> These examples show basic structure only.

### Accuracy When Counting Distinct Values

When counting distinct values in a data stream, particularly when there are repeated elements in a limited memory environment, limitations exist in the accuracy of the count to avoid consuming too much memory in the process. For example, if counting 1,000,000 (million) events. If each event contains a different value, then memory is required to store the count for each of those million entries. Even if the field is only 10 bytes long, that is approximate 9MB of memory required to store the state. In LogScale, this affects the limits as outlined in [State Sizes and Limits](https://library.humio.com/logscale-architecture/training-arch-op-search.html#training-arch-op-search-limits). As noted in that section, LogScale uses an estimation algorithm that produces an estimate of the number of distinct values while keeping the memory usage to a minimum. 

While the algorithm in question doesn't give any guarantees on the relative error of the reported result, the typical accuracy (standard error) is less than 2%, with 2/3s of all results being within 1%, tests with up to 10^7 distinct values, the result at worst deviated by less than 0.02%. The worst results for each test can be seen in the table below: 

Distinct Values| Result of distinct count| Deviation percentage  
---|---|---  
10| 10| 0  
100| 100| 0  
1000| 995| -0.005025125628  
10000| 10039| 0.003884849089  
100000| 100917| 0.009086675189  
1000000| 984780| -0.01545522858  
10000000| 10121302| 0.01198482172  
  
### Important

For less than 100 distinct values, the deviation percentage will be exacerbated. For example, if there are only 10 distinct values, a deviation of 1 is 10%, even though it is the smallest possible deviation from the actual number of distinct values. 

More typically, values used for aggregations or counts for distinct values will have low cardinality (for example, a small number of distinct values against the overall set). 

#### [`count()`](functions-count.html "count\(\)") Syntax Examples

Below are several examples using the [`count()`](functions-count.html "count\(\)") function. Some are simple and others are more complex, with functions embedded within others. 

##### Count All Events

This a simple example using the [`count()`](functions-count.html "count\(\)") function. The query just counts the number of events found in the repository for the period of time selected: 

logscale
    
    
    count()

The result is just a single number, the total count. 

_count  
---  
3886817  
  
To format adding a thousands separator: 

logscale
    
    
    count()
    | format("%,i", field=_count, as=_count)

Produces 

_count|   
---|---  
3| 886,817  
  
##### Group & Count

In this example, the query uses the [`count()`](functions-count.html "count\(\)") function within the [`groupBy()`](functions-groupby.html "groupBy\(\)") function. The first parameter given is the field upon which to group the data. In this case, it's the HTTP method (for example, `GET`, `PUT`, `POST`). The second parameter says to use the function [`count()`](functions-count.html "count\(\)") to count the number occurrences for each method found. 

logscale
    
    
    groupBy(field=method, function=count())

The result is a table with the column headings, method and _count, with the values for each: 

method| _count  
---|---  
DELETE| 7375  
GET| 153493  
POST| 31654  
  
##### Chart of Daily Counts

![count\(\) Chart of Daily Counts](images/query-functions/query-function-count-ex-3.png)  
---  
  
**Figure 148.[`count()`](functions-count.html "count\(\)") Chart of Daily Counts**

  


You can use the [`count()`](functions-count.html "count\(\)") function in conjunction with the [`timeChart()`](functions-timechart.html "timeChart\(\)") function to count the number occurrences of events or other factors. By default, the [`timeChart()`](functions-timechart.html "timeChart\(\)") function will aggregate the data by day. The results will look something like what you see in the screenshot shown in [Figure 148, “`count()` Chart of Daily Counts”](functions-count.html#figure_functions-count-chart-of-daily-counts "Figure 148. count\(\) Chart of Daily Counts"). 

logscale
    
    
    timeChart(function=count())

##### Table of Daily Counts

When a user accesses a web site, the event is logged with a status. For instance, the status code `200` is returned when the request is successful, and `404` when the page is not found. To get a list of status codes returned and a count of each for a given period, you would enter the following query in the Search box: 

logscale
    
    
    groupBy(field=status, function=count())

The sample output is shown below: 

status| _count  
---|---  
101| 9  
200| 55258  
204| 137834  
307| 2  
400| 2  
401| 4  
403| 57  
404| 265  
504| 62  
stopping| 6  
success| 6  
  
### [`count()`](functions-count.html "count\(\)") Examples

Click + next to an example below to get the full details.

####  Aggregate Status Codes by [`count()`](functions-count.html "count\(\)") per Minute 

****

##### Query

logscale
    
    
    bucket(1min, field=status_code, function=count())

##### Introduction

Counts different HTTP status codes over time and buckets them into time intervals of 1 minute. Notice we group by two fields: status code and the implicit field _bucket. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bucket(1min, field=status_code, function=count())

Sets the bucket interval to 1 minute, aggregating the count of the field status_code. 

  3. Event Result set.




##### Summary and Results

Bucketing allows for data to be collected according to a time range. Using the right aggregation function to quantify the value groups that information into the buckets suitable for graphing for example with a [`Bar Chart`](widgets-barchart.html "Bar Chart"), with the size of the bar using the declared function result, [`count()`](functions-count.html "count\(\)") in this example. 

#### Aggregate Status Codes by [`count()`](functions-count.html "count\(\)") Per Minute

**Time series aggregate status codes by[`count()`](functions-count.html "count\(\)") per minute into buckets **

##### Query

logscale
    
    
    bucket(1min, field=status_code, function=count())

##### Introduction

In this example, the [`bucket()`](functions-bucket.html "bucket\(\)") function is used with [`count()`](functions-count.html "count\(\)") to count different HTTP status codes over time and bucket them into time intervals of 1 minute. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bucket(1min, field=status_code, function=count())

Counts different HTTP status codes over time and buckets them into time intervals of 1 minute. Notice that we group by two fields: status_code field and the implicit field _bucket. 

  3. Event Result set.




##### Summary and Results

The query is used to optimizing data storage and query performance. Bucketing allows for data to be collected according to a time range. Using the right aggregation function to quantify the value groups that information into the buckets suitable for graphing for example with a [`Bar Chart`](widgets-barchart.html "Bar Chart"), with the size of the bar using the declared function result, [`count()`](functions-count.html "count\(\)") in this example. 

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

#### Bucket Events Summarized by [`count()`](functions-count.html "count\(\)")

****

##### Query

logscale
    
    
    bucket(function=count())

##### Introduction

Divides the search time interval into buckets. As time span is not specified, the search interval is divided into 127 buckets. Events in each bucket are counted: 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bucket(function=count())

Summarizes events using the [`count()`](functions-count.html "count\(\)") into buckets across the selected timespan. 

  3. Event Result set.




##### Summary and Results

This query organizes data into buckets according to the count of events. 

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

#### Calculate a Percentage of Successful Status Codes Over Time

****

##### Query

logscale
    
    
    | success := if(status >= 500, then=0, else=1)
    | timeChart(series=customer,function=
    [
      {
        [sum(success,as=success),count(as=total)]
    | pct_successful := (success/total)*100
    | drop([success,total])}],span=15m,limit=100)

##### Introduction

Calculate a percentage of successful status codes inside the [`timeChart()`](functions-timechart.html "timeChart\(\)") function field. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         | success := if(status >= 500, then=0, else=1)

Adds a success field at the following conditions: 

     * If the value of field status is greater than or equal to `500`, set the value of success to `0`, otherwise to `1`. 

  3. logscale
         
         | timeChart(series=customer,function=
         [
           {
             [sum(success,as=success),count(as=total)]

Creates a new timechart, generating a new series, customer that uses a compound function. In this example, the embedded function is generating an array of values, but the array values are generated by an embedded aggregate. The embedded aggregate (defined using the `{}` syntax), creates a [`sum()`](functions-sum.html "sum\(\)") and [`count()`](functions-count.html "count\(\)") value across the events grouped by the value of success field generated from the filter query. This is counting the `1`1 or `0` generated by the [`if()`](functions-if.html "if\(\)") function; counting all the values and adding up the ones for successful values. These values will be assigned to the success and total fields. Note that at this point we are still within the aggregate, so the two new fields are within the context of the aggregate, with each field being created for a corresponding success value. 

  4. logscale
         
         | pct_successful := (success/total)*100

Calculates the percentage that are successful. We are still within the aggregate, so the output of this process will be an embedded set of events with the total and success values grouped by each original HTTP response code. 

  5. logscale
         
         | drop([success,total])}],span=15m,limit=100)

Still within the embedded aggregate, drop the total and success fields from the array generated by the aggregate. These fields were temporary to calculate the percentage of successful results, but are not needed in the array for generating the result set. Then, set a span for the buckets for the events of 15 minutes and limit to 100 results overall. 

  6. Event Result set.




##### Summary and Results

This query shows how an embedded aggregate can be used to generate a sequence of values that can be formatted (in this case to calculate percentages) and generate a new event series for the aggregate values. 

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
  
#### Count Events per Repository

**Count of the events received by repository**

##### Query

logscale
    
    
    bucket(span=1d,field=#repo,function=count())
    | @timestamp:=_bucket
    | drop(_bucket)

##### Introduction

Count of X events received by a repo (Cloud). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bucket(span=1d,field=#repo,function=count())

Buckets the values, using the field #repo using a [`count()`](functions-count.html "count\(\)")

  3. logscale
         
         | @timestamp:=_bucket

Updates the timestamp to the value generated by the [`bucket()`](functions-bucket.html "bucket\(\)")

  4. logscale
         
         | drop(_bucket)

Discards the _bucket field from the results. 

  5. Event Result set.




##### Summary and Results

The query can be run on each repo. Or, create a view that looks across multiple repos and then run it from there to get all the repo counts in one search. 

#### Count Total of Malware and Nonmalware Events

**Count total of malware and nonmalvare events in percentage**

##### Query

logscale
    
    
    [count(malware, as=_malware), count(nonmalware, as=_nonmalware)]
    | total := _malware + _nonmalware
    | nonmalware_pct_total := (_nonmalware/total)*100
    | malware_pct_total := (_malware/total)*100

##### Introduction

It is possible to use the [`count()`](functions-count.html "count\(\)") function to show the count in percentage of two fields against total. In this example, the function [`count()`](functions-count.html "count\(\)") function is used to count the field malware and the field nonmalware and have the results returned in percentage. A result set could, for example, be normalware 30% and nonmalware 70%. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         [count(malware, as=_malware), count(nonmalware, as=_nonmalware)]

Returns the counted results of the field malware in a field named _malware and the counted results of the field nonmalware in a field named _nonmalware. 

  3. logscale
         
         | total := _malware + _nonmalware

Assigns the total of these events to a new field named total. 

  4. logscale
         
         | nonmalware_pct_total := (_nonmalware/total)*100
         | malware_pct_total := (_malware/total)*100

Calculates the _malware and _nonmalware as a percentage of the total. 

  5. Event Result set.




##### Summary and Results

The query is used to get an overview of the total number of malware versus nonmalvare. 

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
  
#### Create Time Chart Widget for All Events

****

##### Query

logscale
    
    
    timeChart(span=1h, function=count())

##### Introduction

The [Time Chart](widgets-timechart.html "Time Chart") is the most commonly used widget in LogScale. It displays bucketed time series data on a timeline. The [`timeChart()`](functions-timechart.html "timeChart\(\)") function is used to create time chart widgets, in this example a timechart that shows the number of events per hour over the last 24 hours. We do this by selecting to search over the last 24 hours in the time selector in the UI, and then we tell the function to make each time bucket one hour long (with`span=1hour`). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         timeChart(span=1h, function=count())

Creates 24 time buckets when we search over the last 24 hours, and all searched events get sorted into groups depending on the bucket they belong to (based on their @timestamp  value). When all events have been divided up by time, the [`count()`](functions-count.html "count\(\)") function is run on each group, giving us the number of events per hour. 

  3. Event Result set.




##### Summary and Results

The query is used to create timechart widgets showing number of events per hour over the last 24 hours. The timechart shows one group of events per time bucket. When viewing and hovering over the buckets within the time chart, the display will show the precise value and time for the displayed bucket, with the time showing the point where the bucket starts. 

#### Create Time Chart Widget for Different Events

****

##### Query

logscale
    
    
    timeChart(span=1h, function=count(), series=method)

##### Introduction

The [Time Chart](widgets-timechart.html "Time Chart") is the most commonly used widget in LogScale. It displays bucketed time series data on a timeline. The [`timeChart()`](functions-timechart.html "timeChart\(\)") function is used to create time chart widgets, in this example a timechart that shows the number of the different events per hour over the last 24 hours. For example, you may want to count different kinds of HTTP methods used for requests in the logs. If those are stored in a field named method, you can use this field as a `series`. Furthermore, we select to search over the last 24 hours in the time selector in the UI, and also add a function to make each time bucket one hour long (with`span=1hour`). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         timeChart(span=1h, function=count(), series=method)

Creates 24 time buckets when we search over the last 24 hours, and all searched events get sorted into groups depending on the bucket they belong to (based on their @timestamp  value). When all events have been divided up by time, the [`count()`](functions-count.html "count\(\)") function is run on the series field to return the number of each different kinds of events per hour. 

  3. Event Result set.




##### Summary and Results

The query is used to create timechart widgets showing number of different kinds of events per hour over the last 24 hours. In this example we do not just have one group of events per time bucket, but multiple groups: one group for every value of method that exists in the timespan we are searching in. So if we are still searching over a 24 hour period, and we have received only `GET`, `PUT`, and `POST` requests in that timespan, we will get three groups of events per bucket (because we have three different values for method) Therefore, we end up with 72 groups of events. And every group contains only events which correspond to some time bucket and a specific value of method. Then [`count()`](functions-count.html "count\(\)") is run on each of these groups, to give us the number of `GET` events per hour, `PUT` events per hour, and `POST` events per hour. When viewing and hovering over the buckets within the time chart, the display will show the precise value and time for the displayed bucket, with the time showing the point where the bucket starts. 

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
