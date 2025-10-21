# bucket() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-bucket.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Jun 11, 2025

## [`bucket()`](functions-bucket.html "bucket\(\)")

Extends the [`groupBy()`](functions-groupby.html "groupBy\(\)") function for grouping by time, diving the search time interval into buckets. Each event is put into a bucket based on its timestamp. 

When using the [`bucket()`](functions-bucket.html "bucket\(\)") function, events are grouped by a number of notional 'buckets', each defining a timespan, calculated by dividing the time range by the number of required buckets. The function creates a new field, _bucket, that contains the corresponding bucket's start time in milliseconds (UTC time). 

The [`bucket()`](functions-bucket.html "bucket\(\)") function accepts the same parameters as [`groupBy()`](functions-groupby.html "groupBy\(\)"). 

The output from the [`bucket()`](functions-bucket.html "bucket\(\)") is a table and can be used as the input for a variety of [_Widgets_](widgets.html "Widgets"). Alternatively, use the [`timeChart()`](functions-timechart.html "timeChart\(\)") function. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`buckets`_](functions-bucket.html#query-functions-bucket-buckets)|  number| optional[a] |  |  Defines the number of buckets. The time span is defined by splitting the query time interval into this many buckets. 0..1500   
|  | **Minimum**| `1`|   
[ _`field`_](functions-bucket.html#query-functions-bucket-field)|  string| optional[[a]](functions-bucket.html#ftn.table-functions-bucket-optparamfn) |  |  Specifies which fields to group by. Notice that it is possible to group by multiple fields.   
[_`function`_](functions-bucket.html#query-functions-bucket-function)|  array of aggregate functions| optional[[a]](functions-bucket.html#ftn.table-functions-bucket-optparamfn) | `count(as=_count)`|  Specifies which aggregate functions to perform on each group. Default is to count the elements in each group. If several aggregators are listed for the [_`function`_](functions-bucket.html#query-functions-bucket-function) parameter, then their outputs are combined using the rules described for [`stats()`](functions-stats.html "stats\(\)").   
[_`limit`_](functions-bucket.html#query-functions-bucket-limit)|  integer| optional[[a]](functions-bucket.html#ftn.table-functions-bucket-optparamfn) | `10`|  Defines the maximum number of series to produce. A warning is produced if this limit is exceeded, unless the parameter is specified explicitly. It prioritizes the top-N series. The top N value being the series with the highest numerical value attributed to it by the subquery across all fields.   
|  | **Maximum**| [`500`](functions-bucket.html#query-functions-bucket-limit-max-500)|   
[ _`minSpan`_](functions-bucket.html#query-functions-bucket-minspan)|  long| optional[[a]](functions-bucket.html#ftn.table-functions-bucket-optparamfn) |  |  It sets the minimum allowed span for each bucket, for cases where the _`buckets`_ parameter has a high value and therefore the span of each bucket can be so small as to be of no use. It is defined as a [Relative Time Syntax](syntax-time-relative.html "Relative Time Syntax") such as `1hour` or `3 weeks`. _`minSpan`_ can be as long as the search interval at most — if set as longer instead, a warning notifies that the search interval is used as the _`minSpan`_.   
[_`span`_](functions-bucket.html#query-functions-bucket-span)[b]| relative-time| optional[[a]](functions-bucket.html#ftn.table-functions-bucket-optparamfn) | `auto`|  Defines the time span for each bucket. The time span is defined as a [Relative Time Syntax](syntax-time-relative.html "Relative Time Syntax") like `1hour` or `3 weeks`— however, [Anchoring to Specific Time Units](syntax-time-relative.html#syntax-time-relative-advanced-anchor "Anchoring to Specific Time Units") is not supported when defining the time span. If not provided or set to `auto` the search time interval, and thus the number of buckets, is determined dynamically.   
[_`timezone`_](functions-bucket.html#query-functions-bucket-timezone)|  string| optional[[a]](functions-bucket.html#ftn.table-functions-bucket-optparamfn) |  |  Defines the time zone for bucketing. This value overrides _`timeZoneOffsetMinutes`_ which may be passed in the HTTP/JSON query API. For example, `timezone=UTC` or `timezone='+02:00'`. See the full list of timezones supported by LogScale at [Supported Time Zones](syntax-time-timezones.html "Supported Time Zones").   
[_`unit`_](functions-bucket.html#query-functions-bucket-unit)|  array of strings| optional[[a]](functions-bucket.html#ftn.table-functions-bucket-optparamfn) |  |  Each value is a unit conversion for the given column. For instance: `bytes/span` to `Kbytes/day` converts a sum of bytes into Kb/day automatically taking the time span into account. If present, this array must be either length 1 (apply to all series) or have the same length as [_`function`_](functions-bucket.html#query-functions-bucket-function).   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`span`_](functions-bucket.html#query-functions-bucket-span) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`span`_](functions-bucket.html#query-functions-bucket-span) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     bucket("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     bucket(span="value")
> 
> These examples show basic structure only.

### [`bucket()`](functions-bucket.html "bucket\(\)") Function Operation

The [`bucket()`](functions-bucket.html "bucket\(\)") function has specific implementation and operational considerations, outlined below. 

Important

### Anchored time units not supported

You cannot use [Calendar-Based Units](syntax-time-relative.html#syntax-time-relative-advanced-calendar "Calendar-Based Units") and [Anchoring to Specific Time Units](syntax-time-relative.html#syntax-time-relative-advanced-anchor "Anchoring to Specific Time Units") to define the span length in [`bucket()`](functions-bucket.html "bucket\(\)"). 

#### Series Selection in [`bucket()`](functions-bucket.html "bucket\(\)")

The selection is based on the aggregate numerical output across all specified functions and all time buckets, not the series identifiers themselves. 

The [_`limit`_](functions-bucket.html#query-functions-bucket-limit) prioritizes the top-N series. The top N value being the series with the highest numerical value attributed to it by the subquery across all fields. 

Series Selection Process: 

  * The selection is based on the numerical values produced by the subquery/function. 

  * It is not based on the series names. 

  * When multiple functions are used, the function considers all values produced. 




For different examples of top N series selection, see [Find Top N Value of Series - Example 1](https://library.humio.com/examples/examples-timechart-topnvalue-single-function.html) and [Find Top N Value of Series - Example 2](https://library.humio.com/examples/examples-timechart-topnvalue-multi-functions.html). 

#### How [`bucket()`](functions-bucket.html "bucket\(\)") Calculates Buckets 

When generating aggregated buckets against data, the exact number of buckets may not match the expected due to the combination of the query span, requested number of buckets, and available event data. 

For example, given a query displaying buckets for every one minute, but with a query interval of 1 hour starting at 09:17:30, 61 buckets will be created, as represented by the shaded intervals shown in [Figure 147, “Bucket Allocation using bucket()”](functions-bucket.html#figure_query-function-bucket-creation "Figure 147. Bucket Allocation using bucket\(\)"): 

![Bucket Allocation using bucket\)](images/query-functions/query-function-bucket-creation.png)  
---  
  
**Figure 147. Bucket Allocation using bucket()**

  


The buckets are generated, first based on the requested timespan interval or number of buckets, and then on the relevant timespan boundary. For example: 

  * An interval per hour across a day will start at 00:00 

  * An interval of a minute across an hour will start at 09:00:00 




Buckets will contain the following event data: 

  * The first bucket will contain the extracted event data for the relevant timespan (1 bucket per minute from 09:17), but only containing events after query interval. For example, the bucket will start 09:17, but contain only events with a timestamp after 09:17:30 

  * The next 58 buckets will contain the event data for each minute. 

  * Bucket 60 will contain the event data up until 10:17:30. 

  * Bucket 61 will contain any remaining data from the last time interval bucket. 




The result is that the number of buckets returned will be 61, even though the interval is per minute across a one hour boundary. The trailing data will always be included in the output. It may have an impact on the data displayed when [`bucket()`](functions-bucket.html "bucket\(\)") is used in combination with a [`Time Chart`](widgets-timechart.html "Time Chart"). 

### [`bucket()`](functions-bucket.html "bucket\(\)") Examples

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

#### Bucket Counts When Using [`bucket()`](functions-bucket.html "bucket\(\)")

****

##### Query

**Search Repository:** [humio-metrics](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-metrics.html)

logscale
    
    
    bucket(buckets=24, function=sum("count"))
    | parseTimestamp(field=_bucket,format=millis)

##### Introduction

When generating a list of buckets using the [`bucket()`](functions-bucket.html "bucket\(\)") function, the output will always contain one more bucket than the number defined in [_`buckets`_](functions-bucket.html#query-functions-bucket-buckets). This is to accommodate all the values that will fall outside the given time frame across the requested number of buckets. This calculation is due to the events being bound by the bucket in which they have been stored, resulting in [`bucket()`](functions-bucket.html "bucket\(\)") selecting the buckets for the given time range and any remainder. For example, when requesting 24 buckets over a period of one day in the [humio-metrics](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-metrics.html) repository: 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bucket(buckets=24, function=sum("count"))

Buckets the events into 24 groups, using the [`sum()`](functions-sum.html "sum\(\)") function on the count field. 

  3. logscale
         
         | parseTimestamp(field=_bucket,format=millis)

Extracts the timestamp from the generated bucket and convert to a date time value; in this example the bucket outputs the timestamp as an epoch value in the _bucket field. 

  4. Event Result set.




##### Summary and Results

The resulting output shows 25 buckets, the original 24 requested one additional that contains all the data after the requested timespan for the requested number of buckets. 

_bucket| _sum| @timestamp  
---|---|---  
1681290000000| 1322658945428| 1681290000000  
1681293600000| 1879891517753| 1681293600000  
1681297200000| 1967566541025| 1681297200000  
1681300800000| 2058848152111| 1681300800000  
1681304400000| 2163576682259| 1681304400000  
1681308000000| 2255771347658| 1681308000000  
1681311600000| 2342791941872| 1681311600000  
1681315200000| 2429639369980| 1681315200000  
1681318800000| 2516589869179| 1681318800000  
1681322400000| 2603409167993| 1681322400000  
1681326000000| 2690189000694| 1681326000000  
1681329600000| 2776920777654| 1681329600000  
1681333200000| 2873523432202| 1681333200000  
1681336800000| 2969865160869| 1681336800000  
1681340400000| 3057623890645| 1681340400000  
1681344000000| 3144632647026| 1681344000000  
1681347600000| 3231759376472| 1681347600000  
1681351200000| 3318929777092| 1681351200000  
1681354800000| 3406027872076| 1681354800000  
1681358400000| 3493085788508| 1681358400000  
1681362000000| 3580128551694| 1681362000000  
1681365600000| 3667150316470| 1681365600000  
1681369200000| 3754207997997| 1681369200000  
1681372800000| 3841234050532| 1681372800000  
1681376400000| 1040019734927| 1681376400000  
  
#### Bucket Events Into Groups

**Bucket events into 24 groups using the[`count()`](functions-count.html "count\(\)") function and [`bucket()`](functions-bucket.html "bucket\(\)") function **

##### Query

logscale
    
    
    bucket(buckets=24, function=sum("count"))
    | parseTimestamp(field=_bucket,format=millis)

##### Introduction

In this example, the [`bucket()`](functions-bucket.html "bucket\(\)") function is used to request 24 buckets over a period of one day in the [humio-metrics](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-metrics.html) repository. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bucket(buckets=24, function=sum("count"))

Buckets the events into 24 groups spanning over a period of one day, using the [`sum()`](functions-sum.html "sum\(\)") function on the count field. 

  3. logscale
         
         | parseTimestamp(field=_bucket,format=millis)

Extracts the timestamp from the generated bucket and converts the timestamp to a date time value. In this example, the bucket outputs the timestamp as an epoch value in the _bucket field. This results in an additional bucket containing all the data after the requested timespan for the requested number of buckets. 

  4. Event Result set.




##### Summary and Results

The query is used to optimizing data storage and query performance by making et easier to manage and locate data subsets when performing analytics tasks. Note that the resulting outputs shows 25 buckets; the original requested 24 buckets and in addition the bucket for the extracted timestamp. 

Sample output from the incoming example data: 

_bucket| _sum| @timestamp  
---|---|---  
1681290000000| 1322658945428| 1681290000000  
1681293600000| 1879891517753| 1681293600000  
1681297200000| 1967566541025| 1681297200000  
1681300800000| 2058848152111| 1681300800000  
1681304400000| 2163576682259| 1681304400000  
1681308000000| 2255771347658| 1681308000000  
1681311600000| 2342791941872| 1681311600000  
1681315200000| 2429639369980| 1681315200000  
1681318800000| 2516589869179| 1681318800000  
1681322400000| 2603409167993| 1681322400000  
1681326000000| 2690189000694| 1681326000000  
1681329600000| 2776920777654| 1681329600000  
1681333200000| 2873523432202| 1681333200000  
1681336800000| 2969865160869| 1681336800000  
1681340400000| 3057623890645| 1681340400000  
1681344000000| 3144632647026| 1681344000000  
1681347600000| 3231759376472| 1681347600000  
1681351200000| 3318929777092| 1681351200000  
1681354800000| 3406027872076| 1681354800000  
1681358400000| 3493085788508| 1681358400000  
1681362000000| 3580128551694| 1681362000000  
1681365600000| 3667150316470| 1681365600000  
1681369200000| 3754207997997| 1681369200000  
1681372800000| 3841234050532| 1681372800000  
1681376400000| 1040019734927| 1681376400000  
  
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

#### Calculate Relationship Between X And Y Variables - Example 2 

**Calculate the linear relationship between server load and total response size using the[`linReg()`](functions-linreg.html "linReg\(\)") function with [`bucket()`](functions-bucket.html "bucket\(\)") **

##### Query

logscale
    
    
    bucket(function=[ sum(bytes_sent, as=x), avg(server_load_pct, as=y) ])
    | linReg(x=x, y=y)

##### Introduction

In this example, the [`linReg()`](functions-linreg.html "linReg\(\)") function is used to calculate the linear relationship between bytes_sent (`x` variable) and server_load_pct (`y` variable). The example shows the relationship between server load percentage and total response size across time. 

Example incoming data might look like this: 

@timestamp| bytes_sent| server_load_pct  
---|---|---  
2024-01-15T09:00:00Z| 156780| 45.2  
2024-01-15T09:05:00Z| 234567| 52.8  
2024-01-15T09:10:00Z| 189234| 48.6  
2024-01-15T09:15:00Z| 345678| 65.3  
2024-01-15T09:20:00Z| 123456| 42.1  
2024-01-15T09:25:00Z| 278901| 58.7  
2024-01-15T09:30:00Z| 198765| 51.4  
2024-01-15T09:35:00Z| 287654| 59.2  
2024-01-15T09:40:00Z| 167890| 46.8  
2024-01-15T09:45:00Z| 298765| 61.5  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bucket(function=[ sum(bytes_sent, as=x), avg(server_load_pct, as=y) ])

Buckets the data points by time, then calculates the sum of bytes sent for each bucket returning the result in a field named x, and calculates the average server load percentage for each bucket returning the result in a field named y. 

  3. logscale
         
         | linReg(x=x, y=y)

Correlates x with y, showing the relationship between the variables `x` and `y` and outputs the results in fields named _slope (slope value),_intercept (intercept value),_r2 (adjusted R-squared value), and _n (number of data points). These four key values indicate relationship strength and reliability. 

  4. Event Result set.




##### Summary and Results

The query is used to calculate a linear relationship between bytes_sent (`x` variable) and server_load_pct (`y` variable). 

Calculating the relationship between server load percentage and total response size is useful to identify different operational patterns, such as, for example, performance bottlenecks, resource allocation issues, or to identify system optimization opportunities. 

Sample output from the incoming example data: 

_slope| _intercept| _r2| _n  
---|---|---|---  
0.00010617525557193158| 28.934098111407938| 0.991172367336835| 10  
  
_slope is the rate of change between server load and response size. 

_intercept is the baseline relationship value. 

_r2 is the statistical accuracy of the linear model. 

_n is the total number of data points analyzed. 

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

#### Compute Cumulative Aggregation Across Buckets

**Compute a cumulative aggregation across buckets using the[`accumulate()`](functions-accumulate.html "accumulate\(\)") function with [`timeChart()`](functions-timechart.html "timeChart\(\)") **

##### Query

logscale
    
    
    timeChart(span=1000ms, function=sum(value))
    | accumulate(sum(_sum, as=_accumulated_sum))

##### Introduction

In this example, the [`accumulate()`](functions-accumulate.html "accumulate\(\)") function is used with [`timeChart()`](functions-timechart.html "timeChart\(\)") to accumulate values across time intervals. 

Note that the [`accumulate()`](functions-accumulate.html "accumulate\(\)") function must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

@timestamp| key| value  
---|---|---  
1451606301001| a| 5  
1451606301500| b| 6  
1451606301701| a| 1  
1451606302001| c| 2  
1451606302201| b| 6  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         timeChart(span=1000ms, function=sum(value))

Groups data into 1-second buckets over a 4-second period, sums the field value for each bucket and returns the results in a field named _sum. The result is displayed in a timechart. 

  3. logscale
         
         | accumulate(sum(_sum, as=_accumulated_sum))

Calculates a running total of the sums in the _sum field, and returns the results in a field named _accumulated_sum. 

  4. Event Result set.




##### Summary and Results

The query is used to accumulate values across time intervals/buckets. The query is useful for tracking cumulative metrics or identifying trends in the data. 

Sample output from the incoming example data: 

_bucket| _sum| _accumulated_sum  
---|---|---  
1451606300000| 0| 0  
1451606301000| 12| 12  
1451606302000| 8| 20  
1451606303000| 0| 20  
  
The timechart looks like this: 

![Timechart displaying accumulated aggregation across buckets](images/timechart-accumulated-buckets.png)  
---  
  
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

#### Show Percentiles Across Multiple Buckets

****

##### Query

logscale
    
    
    bucket(span=60sec, function=percentile(field=responsetime, percentiles=[50, 75, 99, 99.9]))

##### Introduction

Show response time percentiles over time. Calculate percentiles per minute by bucketing into 1 minute intervals: 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bucket(span=60sec, function=percentile(field=responsetime, percentiles=[50, 75, 99, 99.9]))

Using a 60 second timespan for each bucket, displays the [`percentile()`](functions-percentile.html "percentile\(\)") for the responsetime field. 

  3. Event Result set.




##### Summary and Results

The [`percentile()`](functions-percentile.html "percentile\(\)") quantifies values by determining whether the value is larger than a percentage of the overall values. The output provides a powerful view of the relative significance of a value. Combined in this example with [`bucket()`](functions-bucket.html "bucket\(\)"), the query will generate buckets of data showing the comparative response time for every 60 seconds.
