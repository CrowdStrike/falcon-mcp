# Statement order for better queries | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/writing-queries-write-best-practice.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Write Queries](writing-queries.html)

Content was updated:Jul 22, 2025

## Statement order for better queries

Specificity matters when writing LogScale queries. The more specific you can be when writing a query, the fewer results you will have to sort through and the faster the query will run. Writing queries that run efficiently and reduce the cost of CPU and memory usage must follow an ordered flow through the query pipeline, starting with the repository. 

Find a reduced set of events by filtering first, and then only perform the formatting and modification of the found data as the formatting has to be performed on every event, which can be a CPU intensive process. 

When writing queries, it is best to follow the following process in order: 

  1. Narrow down the search timeframe as much as possible. 

  2. Narrow down the result set starting with [tagged](parsers-tagging.html "Parsing Event Tags") fields (those starting with `#`). 

  3. Continue to filter the data set with remaining Field Values that exist. 

  4. If there is a large number of distinct values after filtering the data set, consider if you need to filter the data set further to reduce the cardinality. 

### Warning

The query can be cancelled for the benefit of the cluster as a whole, because some aggregators in the query create too many rows. This can happen for instance, when [`groupBy()`](functions-groupby.html "groupBy\(\)") or [`stats()`](functions-stats.html "stats\(\)") are given multiple sub-aggregators, each with a high cardinality output. High cardinality fields are fields with many unique values. 

To avoid cardinality issues with query aggregators, try reducing the number of sub-aggregators, or reduce their cardinality (`limit=${limit}`), otherwise this aggregation can lead to performance issues and inaccurate results. 

  5. After you have filtered what you want to see, filter what you do not want to see. 

  6. Utilize any regex needed to filter down the data further, or for unparsed fields. 

  7. Transform the data how you would like with functions like [Math](functions-math.html "Math Query Functions"), [Evaluation](functions-data-manipulation.html "Data Manipulation Query Functions"), [format](functions-formatting.html "Formatting Query Functions"), etc. 

  8. Aggregate the data utilizing any aggregate functions, such as a [`sum()`](functions-sum.html "sum\(\)"), [`top()`](functions-top.html "top\(\)"), or [`groupBy()`](functions-groupby.html "groupBy\(\)"). 

  9. Perform any final visualization processing such as sorting or table functions. 




### Note

In some situations, it may be necessary to perform steps in a different order. For example, transforming data after it has been aggregated, or transforming and visualizing in the same step. 

When optimizing queries, you want to lower the total number of hits and events returned, then focus on lowering the total work cost of the query, and then handle the formatting and output. Monitoring the work and performance and making small changes as you optimized the query will help to get the best overall performance. 

This process in code format looks like this: 

logscale Syntax
    
    
    tag-filters
    | field filters
    | transformations
    | aggregate function
    | post processing of aggregate result

Remember that the order of operations for queries is important. Let's look at an example of a resource-costly query: 

logscale
    
    
    | eval(fStart = @timestamp - 600)
    | eval(fEnd = @timestamp + 600)
    | formatTime("%F %T.%Q", as=Timestamp, field=@timestamp, timezone=UTC)
    | table([fStart, Timestamp, fEnd])

This query is particularly costly because it formats timestamps for **all events in the defined timespan**. 

Specifying a limit of 200 events prior to output transformation will make the query run much faster because it displays only 200 events, thus performing fewer format operations: 

logscale
    
    
    | table([@timestamp],limit=200) // selects the last 200 timestamps by timestamp
    | eval(fStart = @timestamp - 600)
    | eval(fEnd = @timestamp + 600)
    | format("%1$TF %1$TT.%1$TQ", field=[@timestamp], as=Timestamp, timezone=UTC)
    | table([fStart, Timestamp, fEnd])

To check which query format is less expensive, run them both using the same data set. Then check LogScale's measure of their cost by looking at the Work report, found below the query result. The lower the number, the better the result!

Also see [Query statement order](writing-queries-flow.html#writing-queries-flow-order "Query statement order") for more information on the query flow order. 

An extensive collection of query examples is available at [Examples Library](https://library.humio.com/examples/examples.html).
