# Statistics Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-statistics.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Statistics Query Functions

LogScale's statistics functions provide minimum, maximum, range and other statistical calculations on event data. 

**Table: Statistics Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`avg([as], field)`](functions-avg.html "avg\(\)")| [_`field`_](functions-avg.html#query-functions-avg-field)|  |  Calculates the average for a field of a set of events.   
[`count([as], [distinct], [field])`](functions-count.html "count\(\)")| [_`field`_](functions-count.html#query-functions-count-field)|  |  Counts given events.   
[`max([as], field, [type])`](functions-max.html "max\(\)")| [_`field`_](functions-max.html#query-functions-max-field)|  |  Finds the largest number for the specified field over a set of events.   
[`min([as], field, [type])`](functions-min.html "min\(\)")| [_`field`_](functions-min.html#query-functions-min-field)|  |  Finds the smallest number for the specified field over a set of events.   
[`percentile([accuracy], [as], field, [percentiles])`](functions-percentile.html "percentile\(\)")| [_`field`_](functions-percentile.html#query-functions-percentile-field)|  |  Finds one event with a field for each percentile specified.   
[`range([as], field)`](functions-range.html "range\(\)")| [_`field`_](functions-range.html#query-functions-range-field)|  |  Finds numeric range between smallest and largest numbers for field over a set of events.   
[`sample([field], [percentage])`](functions-sample.html "sample\(\)")| [_`percentage`_](functions-sample.html#query-functions-sample-percentage)|  |  Samples the event stream.   
[`session([function], [maxpause])`](functions-session.html "session\(\)")| [_`function`_](functions-session.html#query-functions-session-function)|  |  Collects events into sessions, and aggregates them.   
[`stats([function])`](functions-stats.html "stats\(\)")| [_`function`_](functions-stats.html#query-functions-stats-function)|  |  Used to compute multiple aggregate functions over the input.   
[`stdDev([as], field)`](functions-stddev.html "stdDev\(\)")| [_`field`_](functions-stddev.html#query-functions-stddev-field)|  |  Calculates the standard deviation for a field over a set of events.
