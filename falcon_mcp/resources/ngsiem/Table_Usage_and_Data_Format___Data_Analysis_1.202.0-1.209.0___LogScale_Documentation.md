# Table Usage and Data Format | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/widgets-table-usage-data.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Data Visualization](data-visualization.html)

/ [Widgets](widgets.html)

/ [Table](widgets-table.html)

### Table Usage and Data Format

This widget is best used with aggregate functions like [`groupBy()`](functions-groupby.html "groupBy\(\)") or [`table()`](functions-table.html "table\(\)") to output a predefined number of fields; for example, a table that displays HTTP `GET` methods and their response time. 

The [`table()`](functions-table.html "table\(\)") function displays data in the order provided by the query, and the [`Table`](widgets-table.html "Table") widget allows to additionally format the information sorted by the function. 

Having a service that produces these logs: 

ini
    
    
    2018-10-10T01:10:11.322Z [ERROR] Invalid User ID. errorID=2, userId=10
    2018-10-10T01:10:12.172Z [WARN]  Low Disk Space.
    2018-10-10T01:10:14.122Z [ERROR] Invalid User ID. errorID=2, userId=11
    2018-10-10T01:10:15.312Z [ERROR] Connection Dropped. errorID=112 server=120.100.121.12
    2018-10-10T01:10:16.912Z [INFO]  User Login. userId=11

To figure out which errors occur most often and show them in a table on one of the dashboards, use a query like this: 

logscale
    
    
    loglevel = ERROR
    | groupBy(errorID, function=[count(as=Count), collect(message)])
    | rename(errorID, as="Error ID")
    | table(["Error ID", message])

The query performs the following operations: 

  * Counts the number of errors bucketed by their errorId. 

  * Shows a human readable message in the table and not just the ID by using the [`collect()`](functions-collect.html "collect\(\)") function, to ensure that the value of the message field makes it through the groupBy phase — which otherwise only includes the series field (errorId) and the result of the aggregate function ([`count()`](functions-count.html "count\(\)"). 

  * Renames the errorID field to Error ID as this will be the header in the table. 

  * Sorts the columns order by using the [`table()`](functions-table.html "table\(\)") function.
