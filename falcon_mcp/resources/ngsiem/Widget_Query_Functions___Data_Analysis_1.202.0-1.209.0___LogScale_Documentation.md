# Widget Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-widget.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Widget Query Functions

LogScale's widget functions provide a direct interface to the corresponding Widgets. For more information, see [_Widgets_](widgets.html "Widgets"). 

**Table: Widget Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`sankey(source, target, [weight])`](functions-sankey.html "sankey\(\)")|  |  |  Produces data compatible with Sankey widget.   
[`table(fields, [limit], [order], [reverse], [sortby], [type])`](functions-table.html "table\(\)")| [_`fields`_](functions-table.html#query-functions-table-fields)|  |  Used to create a widget to present the data in a table.   
[`timeChart([buckets], [function], [limit], [minSpan], [series], [span], [timezone], [unit])`](functions-timechart.html "timeChart\(\)")| [_`series`_](functions-timechart.html#query-functions-timechart-series)|  |  Used to draw a linechart where the x-axis is time.   
[`worldMap([ip], [lat], [lon], [magnitude], [precision])`](functions-worldmap.html "worldMap\(\)")|  |  |  Used to produce data compatible with the World Map widget.
