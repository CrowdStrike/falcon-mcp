# Preamble Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-preamble.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Preamble Query Functions

LogScale's preamble query functions set parameters for the whole query. 

Preamble query functions must appear in the preamble of the query — that is, before any other functions, filters, free-text searches, etc. The functions do not process events. 

### Note

Some preamble functions have additional constraints on their placement in the preamble. These constraints will be described on the documentation page for the relevant functions. 

As an example, the `setTimeInteval()` function should always come before the [`defineTable()`](functions-definetable.html "defineTable\(\)") function. 

**Table: Preamble Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`defineTable([end], include, name, query, [start], [view])`](functions-definetable.html "defineTable\(\)")| [_`query`_](functions-definetable.html#query-functions-definetable-query)|  |  Runs a subquery to generate an in-memory table, then the table results are passed to a primary query to perform join-like operations.   
[`setTimeInterval([end], start, [timezone])`](functions-settimeinterval.html "setTimeInterval\(\)")| [_`start`_](functions-settimeinterval.html#query-functions-settimeinterval-start)|  |  Overwrites the time interval from API/UI.
