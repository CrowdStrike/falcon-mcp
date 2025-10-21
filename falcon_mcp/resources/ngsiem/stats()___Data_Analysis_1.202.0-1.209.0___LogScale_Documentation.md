# stats() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-stats.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`stats()`](functions-stats.html "stats\(\)")

Used to compute multiple aggregate functions over the input. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`function`_](functions-stats.html#query-functions-stats-function)[a]| array of aggregate functions| optional[b] | `count(as=_count)`|  Specifies which aggregate functions to perform on each group.   
[a] The parameter name [_`function`_](functions-stats.html#query-functions-stats-function) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`function`_](functions-stats.html#query-functions-stats-function) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     stats("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     stats(function="value")
> 
> These examples show basic structure only.

### [`stats()`](functions-stats.html "stats\(\)") Function Operation

The [`stats()`](functions-stats.html "stats\(\)") function is implicitly present in a fair number of places where a list of subaggregators is given - for example, `groupBy(x, function=[min(y), max(y)])` is equivalent to `groupBy(x, function=stats([min(y), max(y)]))`. This is how aggregator results are combined when using those other functions. 

The output of [`stats()`](functions-stats.html "stats\(\)") is: 

  * In case all subaggregators yield at most one row of output (this includes most numerical aggregators), the result will be one combined row. 

  * When one or more of the subaggregators of [`stats()`](functions-stats.html "stats\(\)") emit more than one result row, the total output is the _Cartesian product_ of all of the subaggregators' outputs, except if any of the subaggregators outputs zero rows, it is taken as it is outputting a single empty row. 

  * The output combination is checked for fieldname collisions \- and it is an error if a field is present in multiple outputs with conflicting values. 




The [`stats()`](functions-stats.html "stats\(\)") is also available as a shorthand syntax by writing a list of aggregators in square brackets: 

logscale Syntax
    
    
    ...
    | stats(function=[min(), max()])

Is equivalent to: 

logscale Syntax
    
    
    ...
    | [min(),max()]

This produces one row of data that contains both min and max results. 

The following query is equivalent to just [`count()`](functions-count.html "count\(\)"): 

logscale
    
    
    stats(function=count())

### [`stats()`](functions-stats.html "stats\(\)") Examples

Click + next to an example below to get the full details.

#### Annotate Events With Aggregation - Example 1

**Annotate events using[`stats()`](functions-stats.html "stats\(\)") function and aggregation **

##### Query

logscale
    
    
    kvParse()
    | stats([
    avg(x),
    table([x])
    ])

##### Introduction

In this example, the [`stats()`](functions-stats.html "stats\(\)") function is used with aggregation on the field x. 

Example incoming data might look like this: 

x=1  
---  
x=2  
x=9  
x=10  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         kvParse()

Parses the string into key value pairs. 

  3. logscale
         
         | stats([
         avg(x),
         table([x])
         ])

Computes the aggregate functions [`avg()`](functions-avg.html "avg\(\)") and [`table()`](functions-table.html "table\(\)") over the field x, and returns the results in a field named _avg and a field named x. Note that the [`table()`](functions-table.html "table\(\)") function returns more rows as output, whereas the [`avg()`](functions-avg.html "avg\(\)") function only returns 1 row. 

  4. Event Result set.




##### Summary and Results

The query is used to compute multiple aggregate functions over an input. 

Sample output from the incoming example data: 

_avg| x  
---|---  
5.5| 1  
5.5| 2  
5.5| 9  
5.5| 10  
  
#### Annotate Events With Aggregation - Example 2

**Annotate events using[`stats()`](functions-stats.html "stats\(\)") function and aggregation **

##### Query

logscale
    
    
    kvParse()
    | stats([
    sum(x, as=sumX),
    avg(y, as=avgY),
    table([x, y])
    ])

##### Introduction

In this example, the [`stats()`](functions-stats.html "stats\(\)") function is used with aggregation on the field x where one of the subaggregators ([`avg(y)`](functions-avg.html "avg\(\)")) outputs zero rows. 

The example shows what happens, when a subaggregator `avg(y)` does not produce an output. 

Example incoming data might look like this: 

logscale
    
    
    "x=1 y=N/A"
    "x=2 y=N/A"

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         kvParse()

Parses the string into key value pairs. 

  3. logscale
         
         | stats([
         sum(x, as=sumX),
         avg(y, as=avgY),
         table([x, y])
         ])

Computes the aggregate functions [`sum()`](functions-sum.html "sum\(\)"), [`avg()`](functions-avg.html "avg\(\)") and [`table()`](functions-table.html "table\(\)") over the fields x and y, and returns the results in a field named sumX, a field named x, and a field named y. 

  4. Event Result set.




##### Summary and Results

The query is used to compute multiple aggregate functions over an input. 

Sample output from the incoming example data: 
    
    
    "sumX","x","y"
    "3","1","N/A"
    "3","2","N/A"

#### Annotate Events With Aggregation - Example 3

**Annotate events using[`stats()`](functions-stats.html "stats\(\)") function and aggregation **

##### Query

logscale
    
    
    kvParse()
    | stats([
    table([x,y]),
    table([z])
    ])

##### Introduction

In this example, the [`stats()`](functions-stats.html "stats\(\)") function is used with aggregation on the fields x, y, and z, where all of the subaggregators output rows. 

The example shows a Cartesian product where the output is all combinations of all results of the subaggregators 

Example incoming data might look like this: 

logscale
    
    
    "x=1 y=10 z=100"
    "x=2 y=20 z=200"

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         kvParse()

Parses the string into key value pairs. 

  3. logscale
         
         | stats([
         table([x,y]),
         table([z])
         ])

Computes the aggregate function [`table()`](functions-table.html "table\(\)") over the fields x, y, and z, and returns the results - a combination of all outputs, also called the Cartesian product - in a field named x, a field named y, and a field named z. Note that since both subaggregators output multiple rows, the returned result is the Cartesian product, containing all combinations of the results from the subaggregators. 

  4. Event Result set.




##### Summary and Results

The query is used to compute multiple aggregate functions over an input. 

Sample output from the incoming example data: 

x| y| z  
---|---|---  
1| 10| 100  
1| 10| 200  
2| 20| 100  
2| 20| 200  
  
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

#### Count Total Events

**Count total events using the[`stats()`](functions-stats.html "stats\(\)") function **

##### Query

logscale
    
    
    stats(function=count())

##### Introduction

In this example, the [`stats()`](functions-stats.html "stats\(\)") is used with [`count()`](functions-count.html "count\(\)") to calculate the total number of events in the result set. 

Example incoming data might look like this: 

@timestamp| status_code| endpoint| response_time  
---|---|---|---  
1686837825000| 200| /api/users| 145  
1686837826000| 404| /api/products| 89  
1686837827000| 200| /api/orders| 167  
1686837828000| 500| /api/payment| 890  
1686837829000| 200| /api/users| 156  
1686837830000| 404| /api/items| 78  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         stats(function=count())

Counts the total number of events in the result set. The [`count()`](functions-count.html "count\(\)") function is passed as an argument to [`stats()`](functions-stats.html "stats\(\)") and returns the count in a field named _count. 

The query is actually equivalent to just [`count()`](functions-count.html "count\(\)"). 

  3. Event Result set.




##### Summary and Results

The query is used to get a simple count of the total number of events matching the query. 

This query is useful, for example, to monitor event volumes, verify data ingestion, or get quick counts of specific event types when combined with filters. 

Sample output from the incoming example data: 

_count  
---  
6  
  
Note that only one row is returned containing the total count
