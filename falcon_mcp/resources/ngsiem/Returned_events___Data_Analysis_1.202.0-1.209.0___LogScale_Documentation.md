# Returned events | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/writing-queries-tail.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Write Queries](writing-queries.html)

## Returned events

When LogScale returns results, the results must have been aggregated through an [Aggregate Function](functions-aggregate.html "Aggregate Query Functions") for them to be displayed. This is to reduce the number of events that are returned in the final result set. 

If an aggregation is not included in the submitted query, then LogScale adds the aggregation `tail(200)` to limit the default result set to 200 events. 

### Note

When querying within the UI, LogScale may indicate that more results are available by allowing you to download more events. 

This limit on the results applies both to the main query and subqueries. To get a larger a larger result set without an aggregate, manually add a larger value to [`tail()`](functions-tail.html "tail\(\)") to increase the number of results. 

The maximum number of results that can be returned is set by the _`StateRowLimit`_. To automatically use this maximum value, use [`tail(max)`](functions-tail.html "tail\(\)").
