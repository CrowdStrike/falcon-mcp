# Aggregate Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-aggregate.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Aggregate Query Functions

LogScale's aggregate query functions provide grouping and/or aggregation of event data. 

**Table: Aggregate Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`accumulate([current], function)`](functions-accumulate.html "accumulate\(\)")| [_`function`_](functions-accumulate.html#query-functions-accumulate-function)|  |  Applies an aggregation function cumulatively to a sequence of events.   
[`array:intersection(array, [as])`](functions-array-intersection.html "array:intersection\(\)")| [_`array`_](functions-array-intersection.html#query-functions-array-intersection-array)|  |  Determines the set intersection of array values over input events.   
[`array:reduceAll(array, function, var)`](functions-array-reduceall.html "array:reduceAll\(\)")| [_`array`_](functions-array-reduceall.html#query-functions-array-reduceall-array)|  |  Computes a value from all events and array elements of the specified array.   
[`array:reduceColumn(array, [as], function, var)`](functions-array-reducecolumn.html "array:reduceColumn\(\)")| [_`array`_](functions-array-reducecolumn.html#query-functions-array-reducecolumn-array)|  |  Computes an aggregate value for each array element with the same index.   
[`array:union(array, [as])`](functions-array-union.html "array:union\(\)")| [_`array`_](functions-array-union.html#query-functions-array-union-array)|  |  Determines the set union of array values over input events.   
[`avg([as], field)`](functions-avg.html "avg\(\)")| [_`field`_](functions-avg.html#query-functions-avg-field)|  |  Calculates the average for a field of a set of events.   
[`bucket([buckets], [field], [function], [limit], [minSpan], [span], [timezone], [unit])`](functions-bucket.html "bucket\(\)")| [_`span`_](functions-bucket.html#query-functions-bucket-span)|  |  Extends the [`groupBy()`](functions-groupby.html "groupBy\(\)") function for grouping by time.   
[`callFunction([as], field, function)`](functions-callfunction.html "callFunction\(\)")| [_`function`_](functions-callfunction.html#query-functions-callfunction-function)|  |  Calls the named function on a field over a set of events.   
[`collect(fields, [limit], [multival], [separator])`](functions-collect.html "collect\(\)")| [_`fields`_](functions-collect.html#query-functions-collect-fields)|  |  Collects fields from multiple events into one event.   
[`correlate(globalConstraints, includeConstraintValues, includeMatchesOnceOnly, iterationLimit, jitterTolerance, maxPerRoot, query, root, sequence, sequenceBy, within)`](functions-correlate.html "correlate\(\)")| [_`query`_](functions-correlate.html#query-functions-correlate-query)|  |  Correlates data by uniting multiple queries   
[`count([as], [distinct], [field])`](functions-count.html "count\(\)")| [_`field`_](functions-count.html#query-functions-count-field)|  |  Counts given events.   
[`counterAsRate([as], field)`](functions-counterasrate.html "counterAsRate\(\)")| [_`field`_](functions-counterasrate.html#query-functions-counterasrate-field)|  |  Calculates the rate for a counter field.   
[`fieldstats([limit])`](functions-fieldstats.html "fieldstats\(\)")|  |  |  Displays statistics about fields.   
[`groupBy(field, [function], [limit])`](functions-groupby.html "groupBy\(\)")| [_`field`_](functions-groupby.html#query-functions-groupby-field)|  |  Groups events by specified fields and executes aggregate functions on each group.   
[`head([limit])`](functions-head.html "head\(\)")| [_`limit`_](functions-head.html#query-functions-head-limit)|  |  Returns the oldest events from an event stream.   
[`linReg([prefix], x, y)`](functions-linreg.html "linReg\(\)")|  |  |  Computes linear relationship model between two variables using least-squares fitting.   
[`max([as], field, [type])`](functions-max.html "max\(\)")| [_`field`_](functions-max.html#query-functions-max-field)|  |  Finds the largest number for the specified field over a set of events.   
[`min([as], field, [type])`](functions-min.html "min\(\)")| [_`field`_](functions-min.html#query-functions-min-field)|  |  Finds the smallest number for the specified field over a set of events.   
[`neighbor([direction], [distance], include, [prefix])`](functions-neighbor.html "neighbor\(\)")| [_`include`_](functions-neighbor.html#query-functions-neighbor-include)|  |  Allows access to fields from a single neighboring event in a sequence.   
[`partition(condition, function, [split])`](functions-partition.html "partition\(\)")| [_`function`_](functions-partition.html#query-functions-partition-function)|  |  Splits a sequence of events into multiple partitions based on a condition.   
[`percentage([as], condition)`](functions-percentage.html "percentage\(\)")| [_`condition`_](functions-percentage.html#query-functions-percentage-condition)|  |  Calculates what portion of events meet specified conditions.   
[`percentile([accuracy], [as], field, [percentiles])`](functions-percentile.html "percentile\(\)")| [_`field`_](functions-percentile.html#query-functions-percentile-field)|  |  Finds one event with a field for each percentile specified.   
[`range([as], field)`](functions-range.html "range\(\)")| [_`field`_](functions-range.html#query-functions-range-field)|  |  Finds numeric range between smallest and largest numbers for field over a set of events.   
[`rdns([as], field, [limit], [server])`](functions-rdns.html "rdns\(\)")| [_`field`_](functions-rdns.html#query-functions-rdns-field)|  |  Events using RDNS lookup.   
[`sankey(source, target, [weight])`](functions-sankey.html "sankey\(\)")|  |  |  Produces data compatible with Sankey widget.   
[`selectFromMax(field, include)`](functions-selectfrommax.html "selectFromMax\(\)")| [_`field`_](functions-selectfrommax.html#query-functions-selectfrommax-field)|  |  Selects event with the largest value for the specified field.   
[`selectFromMin(field, include)`](functions-selectfrommin.html "selectFromMin\(\)")| [_`field`_](functions-selectfrommin.html#query-functions-selectfrommin-field)|  |  Selects event with the smallest value for the specified field.   
[`selectLast(fields)`](functions-selectlast.html "selectLast\(\)")| [_`fields`_](functions-selectlast.html#query-functions-selectlast-fields)|  |  Specify fields to select from events, keeping value of most recent event for each field.   
[`series(collect, [endmatch], [maxduration], [maxpause], [memlimit], [separator], [startmatch])`](functions-series.html "series\(\)")| [_`collect`_](functions-series.html#query-functions-series-collect)|  |  Collects a series of values for selected fields from multiple events into one or more events.   
[`session([function], [maxpause])`](functions-session.html "session\(\)")| [_`function`_](functions-session.html#query-functions-session-function)|  |  Collects events into sessions, and aggregates them.   
[`slidingTimeWindow([current], function, span, [timestampfield])`](functions-slidingtimewindow.html "slidingTimeWindow\(\)")| [_`function`_](functions-slidingtimewindow.html#query-functions-slidingtimewindow-function)|  |  Applies an aggregation to a moving time-based window of events in a sequence.   
[`slidingWindow([current], events, function)`](functions-slidingwindow.html "slidingWindow\(\)")| [_`function`_](functions-slidingwindow.html#query-functions-slidingwindow-function)|  |  Applies an aggregation to a moving window of a specified number of events in a sequence.   
[`sort([field], [limit], [order], [reverse], [type])`](functions-sort.html "sort\(\)")| [_`field`_](functions-sort.html#query-functions-sort-field)|  |  Sorts events by their fields.   
[`stats([function])`](functions-stats.html "stats\(\)")| [_`function`_](functions-stats.html#query-functions-stats-function)|  |  Used to compute multiple aggregate functions over the input.   
[`stdDev([as], field)`](functions-stddev.html "stdDev\(\)")| [_`field`_](functions-stddev.html#query-functions-stddev-field)|  |  Calculates the standard deviation for a field over a set of events.   
[`sum([as], field)`](functions-sum.html "sum\(\)")| [_`field`_](functions-sum.html#query-functions-sum-field)|  |  Calculates the sum for a field over a set of events.   
[`table(fields, [limit], [order], [reverse], [sortby], [type])`](functions-table.html "table\(\)")| [_`fields`_](functions-table.html#query-functions-table-fields)|  |  Used to create a widget to present the data in a table.   
[`tail([limit])`](functions-tail.html "tail\(\)")| [_`limit`_](functions-tail.html#query-functions-tail-limit)|  |  Returns the newest events from an event stream.   
[`timeChart([buckets], [function], [limit], [minSpan], [series], [span], [timezone], [unit])`](functions-timechart.html "timeChart\(\)")| [_`series`_](functions-timechart.html#query-functions-timechart-series)|  |  Used to draw a linechart where the x-axis is time.   
[`top([as], [error], field, [limit], [max], [percent], [rest], [sum])`](functions-top.html "top\(\)")| [_`field`_](functions-top.html#query-functions-top-field)|  |  Finds the top results based on a given field.   
[`transpose([column], [header], [limit], [pivot])`](functions-transpose.html "transpose\(\)")| [_`pivot`_](functions-transpose.html#query-functions-transpose-pivot)|  |  Transposes a query results set by creating an event for each attribute.   
[`window([buckets], [function], [span])`](functions-window.html "window\(\)")| [_`function`_](functions-window.html#query-functions-window-function)|  |  Computes aggregate functions over a sliding window of data.   
[`worldMap([ip], [lat], [lon], [magnitude], [precision])`](functions-worldmap.html "worldMap\(\)")|  |  |  Used to produce data compatible with the World Map widget.   
  
  


The functions listed in the [Aggregate (for testing) Query Functions](functions-aggregate.html#table_functions-aggregate-testing_summary "Table: Aggregate \(for testing\) Query Functions") table are supported only for testing queries and parsers. 

**Table: Aggregate (for testing) Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`createEvents(rawstring)`](functions-createevents.html "createEvents\(\)")| [_`rawstring`_](functions-createevents.html#query-functions-createevents-rawstring)|  |  Generates temporary events as part of the query.   
  
  


A query becomes an `aggregation query` if it uses at least one aggregate function like [`sum()`](functions-sum.html "sum\(\)"), [`count()`](functions-count.html "count\(\)") or [`avg()`](functions-avg.html "avg\(\)"). 

For example, the query [`count()`](functions-count.html "count\(\)") takes a stream of events as its input, and produces a single record containing a _count field. 

Below are some examples: 

logscale
    
    
    loglevel = ERROR
    | timechart()

logscale
    
    
    x := y * 2
    | bucket(function=sum(x))

### Using Aggregate Query Functions

Aggregate query functions are used to summarize event data during a query. Aggregation simplifies an event set and provides both a shorter set of events and reduces the processing load when querying the event set. For example, when searching for specific events, the events may be summarized by their type or class. By reducing the event data later, parts of the query can be processed more efficiently. 

Aggregation is also used when examining trends and finding patterns and creating sets of data suitable for displaying through a widget such as a bar chart or sankey diagram. For some functions and queries, an aggregate function must be used to summarize the data before it is processed. 

Aggregate functions combine multiple event values into a summarized single value and/or grouped values, reducing many data points into key metrics that can be used for further manipulation, analyzation and visualization. For example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") function summarizes data by one or more fields, and then provides a summary value for that group, such as count, sum, average, minimum, or maximum for all rows in a column or table as defined by the query. 

### Functions Requiring Prior Aggregation

Some functions (for example visualization functions or analysis functions) need summarized or grouped data to create meaningful widgets or to simplify the processing of the incoming data. Processing millions of individual events would create a significant load on the system for relatively small values. For more efficient querying, aggregation creates a smaller set of data on which to perform more intensive processing. 

As an example, you must group the data first using aggregate functions like [`groupBy()`](functions-groupby.html "groupBy\(\)") or [`bucket()`](functions-bucket.html "bucket\(\)") if you are trying to: 

  * Collect events into blocks of time; for example counting the occurrences per minute or hour either in live or static queries. 

  * Show summarized value data (for example: counts, sums, averages). 

  * Create charts through the widgets or other visualizations. 

  * Sort events or matches by count or incidence. 

  * Find the top N values or bottom N values of a list. 




Examples of functions used for visualization could be [`timeChart()`](functions-timechart.html "timeChart\(\)") and [`sankey()`](functions-sankey.html "sankey\(\)"). 

Examples of functions used for analysis could be [`percentage()`](functions-percentage.html "percentage\(\)"), [`top()`](functions-top.html "top\(\)") and [`sort()`](functions-sort.html "sort\(\)"). 

Sequence functions must also come after an aggregator function (for example, [`bucket()`](functions-bucket.html "bucket\(\)"), [`head()`](functions-head.html "head\(\)"),` sort()`) to provide a meaningful order to the events. Order matters in query construction. 

In some cases, if a query is defined so that it requires an aggregate data set, a warning will be generated by LogScale to indicate the aggregate query requirement. For example: 

The partition() function must come after an aggregator. E.g. groupBy(), bucket(), sort(), tail(), or head(). 

### Aggregates as Arguments

For some functions used during a query, the argument used must be an aggregate function. For example, the [`partition()`](functions-partition.html "partition\(\)") function splits a sequence of events into multiple sequences, using an aggregate function to identify each partition. 

Using aggregate functions as arguments enables dynamic calculations and data-driven analysis based on your data patterns. The aggregate functions calculate a value such as count, sum, average, minimum, or maximum for all rows in a column or table as defined by the query. 

In some cases, multiple aggregates can be used together and also be nested for advanced calculations. 

As an example, with [`groupBy()`](functions-groupby.html "groupBy\(\)") you can specify multiple aggregate functions so that the grouped event set contains minimum, maximum and average values for each group.
