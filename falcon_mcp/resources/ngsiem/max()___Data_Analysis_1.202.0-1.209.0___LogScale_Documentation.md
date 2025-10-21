# max() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-max.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`max()`](functions-max.html "max\(\)")

Finds the largest number for the specified field over a set of events. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-max.html#query-functions-max-as)|  string| optional[a] | `_max`|  Name of output field.   
[_`field`_](functions-max.html#query-functions-max-field)[b]| string| required |  |  Field to extract a number from.   
[_`type`_](functions-max.html#query-functions-max-type)|  string| optional[[a]](functions-max.html#ftn.table-functions-max-optparamfn) |  |  description   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-max.html#query-functions-max-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-max.html#query-functions-max-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     max("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     max(field="value")
> 
> These examples show basic structure only.

### [`max()`](functions-max.html "max\(\)") Syntax Examples

Return what was the maximum responsetime: 

logscale
    
    
    max(responsetime)

Filter for events in the repository with maximum responsetime values greater than 5 seconds: 

logscale
    
    
    max(responsetime)
    | _max> 5

### [`max()`](functions-max.html "max\(\)") Examples

Click + next to an example below to get the full details.

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

#### Calculate Minimum and Maximum Response Times

**Calculate minimum and maximum response times using multiple aggregate functions in square brackets**

##### Query

logscale
    
    
    [min_response := min(responsetime), max_response := max(responsetime)]

##### Introduction

In this example, the [`min()`](functions-min.html "min\(\)") and [`max()`](functions-max.html "max\(\)") functions are used to find the shortest and longest response times, with results stored in named fields. 

Square brackets allow multiple aggregations to be performed in a single operation 

Writing a list of aggregators in square brackets is a shorthand syntax for the [`stats()`](functions-stats.html "stats\(\)") function. 

Example incoming data might look like this: 

@timestamp| endpoint| responsetime| status_code  
---|---|---|---  
1686837825000| /api/users| 145| 200  
1686837826000| /api/products| 892| 200  
1686837827000| /api/orders| 167| 200  
1686837828000| /api/payment| 1290| 500  
1686837829000| /api/users| 156| 200  
1686837830000| /api/items| 78| 200  
1686837831000| /api/orders| 934| 200  
1686837832000| /api/checkout| 923| 200  
1686837833000| /api/products| 134| 200  
1686837834000| /api/users| 445| 200  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         [min_response := min(responsetime), max_response := max(responsetime)]

In a single operation, calculates the minimum value from the responsetime field and returns the results in a field named min_response, and calculates the maximum value from the responsetime field and returns the results in a field named max_response. 

Square brackets allow multiple aggregations to be performed in a single operation 

  3. Event Result set.




##### Summary and Results

The query is used to find the range of response times by calculating both the minimum and maximum values. 

The results are returned in fields with names specified in the field assignments 

This query is useful, for example, to monitor service performance, identify outliers in response times, or establish performance baselines. 

Sample output from the incoming example data: 

min_response| max_response  
---|---  
78| 1290  
  
Note that only one row is returned containing both calculated values. 

#### Compute Aggregate Value for Each Array Element With Same Index

**Compute an aggregate value for each array element with the same index using the[`array:reduceColumn()`](functions-array-reducecolumn.html "array:reduceColumn\(\)") **

##### Query

logscale
    
    
    maxTimes := array:reduceColumn(times, var=x, function={time := max(x)})

##### Introduction

In this example, the [`array:reduceColumn()`](functions-array-reducecolumn.html "array:reduceColumn\(\)") function is used to find the maximum time for each array element with same index in a flat array. 

Example incoming data might look like this: 

times[0]| times[1]| times[2]  
---|---|---  
1| 2| 3  
5| 1| 0  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         maxTimes := array:reduceColumn(times, var=x, function={time := max(x)})

Computes the maximum time for each array element with same index in the array and reduces it to one value. 

  3. Event Result set.




##### Summary and Results

The query is used to find the maximum time for each array element with same index in a flat array. 

_reduceColumn[0]| _reduceColumn[1]| _reduceColumn[2]  
---|---|---  
5| 2| 3  
  
#### Compute an Aggregated Value of an Array on All Events

**Compute an aggregated value of a flat array on all events using the[`array:reduceAll()`](functions-array-reduceall.html "array:reduceAll\(\)") function **

##### Query

logscale
    
    
    array:reduceAll("values[]", var=x, function=max(x))

##### Introduction

In this example, the aggregate function [`max()`](functions-max.html "max\(\)") is used to output a single event with a single field. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:reduceAll("values[]", var=x, function=max(x))

Computes the maximum value over all the values within the array values[] by using the [`max()`](functions-max.html "max\(\)") on each element, and then across each event in the event set. 

  3. Event Result set.




##### Summary and Results

The query is used to compute a value from all events and array elements of a specified array. The `reduce()` method is recommended, when you need to have a single value returned from iterating over your array. Only aggregate functions that return a single event with a single field (such as [`avg()`](functions-avg.html "avg\(\)"), [`count()`](functions-count.html "count\(\)"), [`sum()`](functions-sum.html "sum\(\)"), [`max()`](functions-max.html "max\(\)") etc.) are allowed as the [_`function`_](functions-array-reduceall.html#query-functions-array-reduceall-function) argument. 

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
  
#### Find Maximum Value in Field

**Calculate the maximum value in a numeric field using the[`max()`](functions-max.html "max\(\)") function **

##### Query

logscale
    
    
    max(responsetime)

##### Introduction

In this example, the [`max()`](functions-max.html "max\(\)") function is used to find the slowest response time from a set of web server logs. The response time is the time from the receipt of a request to the complete processing of the request. 

Example incoming data might look like this: 

@timestamp| endpoint| responsetime| status  
---|---|---|---  
2025-08-06T10:00:00Z| /api/users| 180| 200  
2025-08-06T10:00:01Z| /api/products| 2850| 200  
2025-08-06T10:00:02Z| /api/orders| 95| 200  
2025-08-06T10:00:03Z| /api/users| 450| 200  
2025-08-06T10:00:04Z| /api/products| 1275| 200  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         max(responsetime)

Calculates the maximum value found in the responsetime field across all events and returns the result in a new field named _max. If server response time is high, it may indicate that the server is overloaded and having difficulties processing requests. 

If no events contain the specified field, or if the field contains non-numeric values, the function returns nothing. 

  3. Event Result set.




##### Summary and Results

The query is used to find the slowest response time in the event set, helping identify potential performance issues. Response time is an important parameter. If server response time is high, it may indicate that the server is overloaded and having difficulties processing requests. 

This query is useful, for example, to identify performance bottlenecks, monitor service level agreement (SLA) breaches, or detect abnormal response times. 

Sample output from the incoming example data: 

_max  
---  
2850  
  
The result shows a response time of 2850ms (2.85 seconds), which falls into the poor performance category and could indicate a significant performance issue requiring investigation. 

Note that the result shows the single largest value found in the responsetime field across all events in the default output field _max. 

The maximum response time can be effectively displayed in a single value widget on a dashboard. For more comprehensive performance analysis, consider combining this with other aggregation functions like [`min()`](functions-min.html "min\(\)") and [`avg()`](functions-avg.html "avg\(\)") to show the full range of response times. For an example, see [Calculate Minimum and Maximum Response Times](https://library.humio.com/examples/examples-min-max-response-squarebrackets.html). 

#### Rounding Within a Timechart

**Round down a number in a field and display information in a timechart using the[`round()`](functions-round.html "round\(\)") and [`timeChart()`](functions-timechart.html "timeChart\(\)") functions **

##### Query

logscale
    
    
    timeChart(function={max(value) | round(_max, how=floor)})timechart(function=max(value))

##### Introduction

In this example, the [`round()`](functions-round.html "round\(\)") function is used with a _`floor`_ parameter to round down a field value to an integer (whole number) and display information within a timechart. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         timeChart(function={max(value) | round(_max, how=floor)})timechart(function=max(value))

Creates a time chart using [`max()`](functions-max.html "max\(\)") as the aggregate function for a field named value to find the highest value in each time bucket, and returns the result in a field named _max. 

Rounds the implied field _max from the aggregate [`max()`](functions-max.html "max\(\)") using the `floor` option to round down the value. 

Example of original _max values: `10.8`, `15.3`, `20.7`. 

After floor: `10`, `15`, `20`. 

  3. Event Result set.




##### Summary and Results

The query is used to round down maximum values over time to nearest integer (whole value). This is useful when displaying information in a time chart. Rounding to nearest integer will make it easier to distinguish the differences between values when used on a graph for time-based visualization. The query simplifies the data presentation. 

### Note

To round to a specific decimal accuracy, the [`format()`](functions-format.html "format\(\)") function must be used. 

![Showing Round with timeChart\(\)](images/timechart-round-max.png)  
---
