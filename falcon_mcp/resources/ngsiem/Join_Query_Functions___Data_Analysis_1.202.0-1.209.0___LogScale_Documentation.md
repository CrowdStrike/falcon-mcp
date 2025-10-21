# Join Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-join-functions.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Join Query Functions

LogScale's join functions enable you to join data from one or more repositories or views into a single table. For more information, see [`join()` Syntax](query-joins-methods-join.html#query-joins-methods-join-syntax "join\(\) Syntax"). 

**Table: Join Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`defineTable([end], include, name, query, [start], [view])`](functions-definetable.html "defineTable\(\)")| [_`query`_](functions-definetable.html#query-functions-definetable-query)|  |  Runs a subquery to generate an in-memory table, then the table results are passed to a primary query to perform join-like operations.   
[`join([end], field, [include], [key], [limit], [live], [max], [mode], query, [repo], [start], [view])`](functions-join.html "join\(\)")| [_`query`_](functions-join.html#query-functions-join-query)|  |  Join two LogScale searches.   
[`selfJoin([collect], field, [limit], [postfilter], [prefilter], [select], where)`](functions-selfjoin.html "selfJoin\(\)")| [_`field`_](functions-selfjoin.html#query-functions-selfjoin-field)|  |  Used to collate data from events that share a key.   
[`selfJoinFilter(field, [prefilter], where)`](functions-selfjoinfilter.html "selfJoinFilter\(\)")| [_`field`_](functions-selfjoinfilter.html#query-functions-selfjoinfilter-field)|  |  Runs query to determine IDs, and then gets all events containing one of them.
